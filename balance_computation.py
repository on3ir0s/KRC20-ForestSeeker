# Copyright (c) 2025 on3ir0s
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import aiohttp
import asyncio
import csv
from disk_io import write_holders_to_csv

# Fetch current balance for an address from API
async def fetch_address_balance(address, tick):
    async with aiohttp.ClientSession() as session:
        current_balance_url = f"https://api.kasplex.org/v1/krc20/address/{address}/token/{tick}"
        retries = 5
        while True:
                for attempt in range(retries):
                    try:
                        async with asyncio.timeout(12):
                            try:
                                async with session.get(current_balance_url) as response:
                                    data = await response.json()
                                    balance_info = data.get("result", [{}])[0]   
                                if response.status != 200:
                                    raise Exception(f"API error with status code {response.status}")
                                return address, balance_info.get("balance", "0") 
                            except Exception as e:
                                print(f"Error: {e}. Retrying... ({attempt + 1}/{retries})")
                                await asyncio.sleep(10)
                                continue
                    except asyncio.TimeoutError:
                        print(f"Error: Request timeout. Retrying... ({attempt + 1}/{retries})")
                        await asyncio.sleep(10)
                else:   
                    # IF API errors continue, return -1 as balance
                    return address, -1

# Function to calculate token balance from transaction file
def calculate_balance(filename, address, tick):
    balance = 0
    minted = 0
    transferred = 0
    listed = 0

    # Read transactions from CSV file
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for txn in reader:
            if txn["opAccept"] == "1" and tick.lower() == txn["tick"].lower():
                if txn["op"] == "deploy":
                    try:
                        pre_int = int(txn["pre"])                        
                    except (ValueError, TypeError):
                        pre_int = 0        
                    pre_int = pre_int / 100000000  
                    minted += float(txn["amt_int"])
                elif txn["op"] == "mint":
                    minted += float(txn["amt_int"])
                elif txn["op"] == "transfer" and txn["from"] == address:
                    transferred -= float(txn["amt_int"])
                elif txn["op"] == "transfer" and txn["to"] == address:
                    transferred += float(txn["amt_int"])
                elif txn["op"] == "list" and txn["from"] == address:
                    listed += float(txn["amt_int"])
                elif txn["op"] == "send" and txn["from"] == address:
                    listed -= float(txn["amt_int"])
                    transferred -= float(txn["amt_int"])                    
                elif txn["op"] == "send" and txn["to"] == address:
                    transferred += float(txn["amt_int"])                    
    balance = minted + transferred - listed
    
    results = asyncio.run(fetch_address_balance(address, tick))
    current_balance_int = int(results[1]) / 100000000

    print(f"\nMinted: {minted}")
    print(f"Transferred: {transferred}")
    print(f"Listed: {transferred}")
    print(f"Current balance from transactions: {balance}")
    print(f"Current balance from API: {current_balance_int}\n")

# Function to process snapshot based on mode ('end' or 'opscore')
def process_holders_snapshot(filename, tick, mode, opscore=None):
    holders = {}
    total_transactions = 0
    accounted_transactions = 0
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for txn in reader:
            total_transactions += 1
            print(f"\rTotal transactions processed: {total_transactions-1} / Total transactions accounted for: {accounted_transactions}", end='')
            if txn["opAccept"] == "1" and tick.lower() == txn["tick"].lower() and (mode == "end" or (mode == "opscore" and int(txn["opScore"]) <= opscore)):
                accounted_transactions += 1
                from_address = txn["from"]
                to_address = txn["to"]
                if txn["op"] == "deploy":
                    holders.setdefault(to_address, {"minted": 0, "transferred": 0, "listed": 0, "balance": 0})
                    holders[to_address]["minted"] += float(txn["pre"]) / 100000000
                elif txn["op"] == "mint":
                    holders.setdefault(to_address, {"minted": 0, "transferred": 0, "listed": 0, "balance": 0})
                    holders[to_address]["minted"] += float(txn["amt_int"])
                elif txn["op"] == "transfer":
                    holders.setdefault(from_address, {"minted": 0, "transferred": 0, "listed": 0, "balance": 0})
                    holders.setdefault(to_address, {"minted": 0, "transferred": 0, "listed": 0, "balance": 0})
                    holders[from_address]["transferred"] -= float(txn["amt_int"])
                    holders[to_address]["transferred"] += float(txn["amt_int"])
                elif txn["op"] == "list":
                    if from_address:
                        holders.setdefault(from_address, {"minted": 0, "transferred": 0, "listed": 0, "balance": 0})
                        holders[from_address]["listed"] += float(txn["amt_int"])
                elif txn["op"] == "send":
                    holders.setdefault(from_address, {"minted": 0, "transferred": 0, "listed": 0, "balance": 0})
                    holders[from_address]["listed"] -= float(txn["amt_int"])
                    holders[from_address]["transferred"] -= float(txn["amt_int"])                    
                    holders.setdefault(to_address, {"minted": 0, "transferred": 0, "listed": 0, "balance": 0})
                    holders[to_address]["transferred"] += float(txn["amt_int"])

    unique_addresses = len(holders)
    print(f"\n\nTotal unique wallets: {unique_addresses}")

    async def fetch_balances(addresses):
            tasks = []
            for address in addresses:
                tasks.append(fetch_address_balance(address, tick))
            results = await asyncio.gather(*tasks)
            return results

    address_list = list(holders.keys())
    processed_addresses = 0
    API_errors = 0
    batch_size = 200
    for i in range(0, unique_addresses, batch_size):
        batch_addresses = address_list[i:i + batch_size]
        results = asyncio.run(fetch_balances(batch_addresses))
        for address, api_balance in results:
            processed_addresses += 1
            print(f"\rProcessing wallet balance: {processed_addresses} / {unique_addresses}", end="")
            holders[address]["balance"] = holders[address]["minted"] + holders[address]["transferred"] - holders[address]["listed"]
            if api_balance == -1:
                API_errors += 1
            try:
                holders[address]["api_balance"] = int(api_balance) / 100000000
                holders[address]["delta"] = holders[address]["api_balance"] - holders[address]["balance"] # final - snapshot
            except Exception as e:
                print(f"\nError: {e}. Returning to main menu.)")
                continue

    wallets_with_balance_gt_zero = sum(1 for holder in holders.values() if holder["balance"] > 0)
    if API_errors > 0:
        print(f"\n\nWarning! {API_errors} error(s) found retrieving the current balance from the Kasplex API")
    print(f"\nTotal unique wallets with balance greater than 0: {wallets_with_balance_gt_zero}")

    if mode == "end":
        write_holders_to_csv(f"snapshot_{tick}_full.csv", holders)
        print(f"\nFile snapshot_{tick}_full.csv successfully witten to the 'files_io' folder")                
    elif mode == "opscore":
        write_holders_to_csv(f"snapshot_{tick}_opscore_{opscore}.csv", holders)
        print(f"\nFile snapshot_{tick}_opscore_{opscore}.csv successfully witten to the 'files_io' folder")
        