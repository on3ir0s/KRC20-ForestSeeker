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
    if address and tick:
        filename = f"transactions_{tick}_{address}.csv"
    elif address:
        filename = f"transactions_all_{address}.csv"
    else: 
        filename = f"transactions_{tick}_full.csv"
        
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
            print ("\n\n\n")
            while True:
                await asyncio.sleep(1)
                current_transactions = total_transactions
                transactions_per_second = current_transactions - prev_transactions
                total_time = time.time() - start_time
                average_speed = total_transactions / total_time
                print(f"\033[F\033[F\033[F\rCurrent processing speed (transactions / sec): {transactions_per_second:.2f} | Average processing speed (transactions / sec): {average_speed:.2f}\nTotal transactions processed: {total_transactions}\nPress CTRL+C and check your network connectivity if 'Total transactions processed' does not increase for more than 20 seconds.")
                prev_transactions = current_transactions

        asyncio.create_task(processing_speed_indicator())

    while True:
        async with session.get(API_URL, params=params) as response:
            if response.status != 200:
                raise Exception(f"API error with status code {response.status}")
            try:
                async with asyncio.timeout(0.95):
                    data = await response.json()
            except TimeoutError:
                raise Exception(f"Data retrieval timeout")
            transactions.extend(data.get("result", []))
            total_transactions += len(data.get("result", []))
            size += sum(len(str(txn)) for txn in data.get("result", []))
            if size >= CHUNK_SIZE:
                write_to_csv(filename, transactions, tick, append=append)
                transactions.clear()
                size = 0
                append = True
            if not data.get("next") or any(txn.get("op") == "deploy" for txn in data.get("result", [])):
                break
            # Update params with 'next' for subsequent requests
            params["next"] = data["next"]
    write_to_csv(filename, transactions, tick, append=append)
    # print() # prints an empty line

# Async function to handle retries
async def retrieve_transactions(address, tick=''):
    retries = 10
    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            try:
                await fetch_transactions(session, tick, address)
                break
            except Exception as e:
                print(f"Error: {e}. Retrying... ({attempt + 1}/{retries})\n\n\n\n")
                await asyncio.sleep(1)
        else:
            print("Failed after 10 retries. Returning to main menu.")

# Async function to retrieve all transactions for a ticker
async def retrieve_all_transactions(tick, address=''):
    retries = 10
    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            try:
                await fetch_transactions(session, tick, address)
                break
            except Exception as e:
                print(f"Error: {e}. Retrying... ({attempt + 1}/{retries})\n\n\n\n")
                await asyncio.sleep(1)
        else:
            print("\nFailed after 10 retries. Returning to main menu.")

# Async function to retrieve transactions from a file of addresses
async def retrieve_transactions_from_file(filename, tick):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        addresses = [row["address"] for row in reader]

    total_addresses = len(addresses)
    processed_addresses = 0

    async def process_batch(session, batch):
        nonlocal processed_addresses
        print(f"\rProcessed wallets: {processed_addresses} / {total_addresses}", end="")
        tasks = [fetch_transactions(session, tick, address, multiple='yes') for address in batch]
        await asyncio.gather(*tasks)
        processed_addresses += len(batch)

    retries = 10
    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            try:
                for i in range(0, total_addresses, 10):
                    batch = addresses[i:i + 10]
                    await process_batch(session, batch)
                break
            except Exception as e:
                print(f"\nError: {e}. Retrying... ({attempt + 1}/{retries})")
                await asyncio.sleep(0.2)
        else:
            print("Failed after 10 retries. Returning to main menu.")
    
    print(f"\rProcessed wallets: {processed_addresses} / {total_addresses}")
