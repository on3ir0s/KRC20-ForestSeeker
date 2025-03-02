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
import os
import time
import csv
from disk_io import write_to_csv

# Constants
API_URL = "https://api.kasplex.org/v1/krc20/oplist"
CHUNK_SIZE = 1024 * 1024  # 1 MB

# Async function to fetch transactions for a single address or all addresses
async def fetch_transactions(session, tick, address, multiple=''):
    transactions = []
    size = 0
    timestr = time.strftime("%Y%m%d-%H%M%S") #add time to filename
    if address and tick:
        filename = f"transactions_{tick}_{address}_{timestr}.csv"
    elif address:
        filename = f"transactions_all_{address}_{timestr}.csv"
    else: 
        filename = f"transactions_{tick}_full_{timestr}.csv"
        
    # Delete existing file if it exists
    if os.path.exists(filename):
        os.remove(filename)
    # Initial request without 'prev' and 'next'
    params = {"tick": tick}
    if address:
        params["address"] = address
    append = False
    total_transactions = 0
    start_time = time.time()

    if multiple != 'yes':
        async def processing_speed_indicator():
            nonlocal total_transactions
            prev_transactions = 0
            # print ("\n\n\n")
            print ("\n\n")
            display_interval = 1
            while True:
                await asyncio.sleep(display_interval)
                current_transactions = total_transactions
                transactions_per_second = current_transactions - prev_transactions
                total_time = time.time() - start_time
                hours, rem = divmod(total_time, 3600)
                minutes, seconds = divmod(rem, 60)
                average_speed = total_transactions / total_time
                print(f"\033[F\033[F\rCurrent processing speed (transactions/s): {(transactions_per_second/display_interval):.2f} | Average processing speed (transactions/s): {average_speed:.2f}\nTotal transactions processed: {total_transactions} | Total time elapsed: {int(hours):02}:{int(minutes):02}:{int(seconds):02} (hh:mm:ss)")
                prev_transactions = current_transactions

        asyncio.create_task(processing_speed_indicator())

    retries = 5
    while True:
        for attempt in range(retries):
            try:
                async with asyncio.timeout(12):
                    try:
                        async with session.get(API_URL, params=params) as response:
                            data = await response.json()
                        if response.status != 200:
                            raise Exception(f"API error with status code {response.status}")
                        transactions.extend(data.get("result", []))
                        total_transactions += len(data.get("result", []))
                        size += sum(len(str(txn)) for txn in data.get("result", []))
                        if size >= CHUNK_SIZE:
                            write_to_csv(filename, transactions, tick, append=append)
                            transactions.clear()
                            size = 0
                            append = True
                        if not data.get("next"):
                            write_to_csv(filename, transactions, tick, append=append)
                            transactions.clear()
                            size = 0
                            append = True
                            return timestr
                        # Update params with 'next' for subsequent requests
                        params["next"] = data["next"]
                    except Exception as e:
                        print(f"Error: {e}. Retrying... ({attempt + 1}/{retries})\n\n\n")
                        await asyncio.sleep(10)
                        continue
                break  # Break out of the retry loop on success
            except asyncio.TimeoutError:
                print(f"Error: Request timeout. Retrying... ({attempt + 1}/{retries})\n\n\n")
                await asyncio.sleep(10)
        else:
            raise Exception(f"Failed after 5 retries, or user interrupt. Returning to main menu.")
            
# Async function to retrieve transactions for a wallet
async def retrieve_transactions(address, tick=''):
    try:
        async with aiohttp.ClientSession() as session:
            timestr = await fetch_transactions(session, tick, address)
            if tick == '':
                print(f"\nFile transactions_all_{address.replace('kaspa:', '')}_{timestr}.csv successfully witten to the 'files_io' folder")
            else:
                print(f"\nFile transactions_{tick}_{address.replace('kaspa:', '')}_{timestr}.csv successfully witten to the 'files_io' folder")
    except:
        print("\nFailed after 5 retries, or user interrupt. Returning to main menu.")

# Async function to retrieve all transactions for a ticker
async def retrieve_all_transactions(tick, address=''):
    try:
        async with aiohttp.ClientSession() as session:
            timestr = await fetch_transactions(session, tick, address)
            print(f"\nFile transactions_{tick}_full_{timestr}.csv successfully witten to the 'files_io' folder")
    except:
        print("\nFailed after 5 retries, or user interrupt. Returning to main menu.")

# Async function to retrieve transactions from a file of addresses
try:
    async def retrieve_transactions_from_file(filename, tick):
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            addresses = [row["address"] for row in reader]

        unique_addresses = list(set(addresses))
        tot_unique_addresses = len(unique_addresses)
        
        processed_addresses = 0

        async def process_batch(session, batch):
            nonlocal processed_addresses
            tasks = [fetch_transactions(session, tick, address, multiple='yes') for address in batch]
            await asyncio.gather(*tasks)
            processed_addresses += len(batch)

        async with aiohttp.ClientSession() as session:
            for i in range(0, tot_unique_addresses, 10):
                batch = unique_addresses[i:i + 10]
                print(f"\rProcessed unique wallets: {processed_addresses} / {tot_unique_addresses}", end="")                    
                await process_batch(session, batch)
            print(f"\rProcessed unique wallets: {processed_addresses} / {tot_unique_addresses}")
            print(f"\nFile(s) transactions_{tick}_[wallet]_[timestamp].csv successfully witten to the 'files_io' folder")
except:
    print("\nFailed after 5 retries, or user interrupt. Returning to main menu.")