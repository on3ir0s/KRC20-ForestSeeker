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

import csv
from datetime import datetime

# Function to sanitize file names
def sanitize_filename(filename):
    filename = filename.replace("kaspa:", "")  # Remove "kaspa:" if present in the filename
    return "".join(c if c.isalnum() or c in (' ', '.', '_') else '_' for c in filename).rstrip()

# Function to convert Unix time to human-readable format
def unix_to_human(unix_time):
    try:
        return datetime.fromtimestamp(unix_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
    except (OSError, OverflowError, ValueError):
        return 'Invalid Timestamp'

# Function to write transactions to CSV
def write_to_csv(filename, transactions, tick, append=False):
    filename = sanitize_filename(filename)
    fieldnames = ["p", "op", "tick", "max", "lim", "dec", "pre", "amt", "amt_int", "from", "to", "opScore", "hashRev", "checkpoint", "feeRev",
                  "txAccept", "opAccept", "opError", "mtsAdd", "mtsMod", "utxo", "price", "mtsAdd_hr", "mtsMod_hr"]
    mode = 'a' if append else 'w'
    with open(filename, mode, newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not append:
            writer.writeheader()
        for txn in transactions:
            amt = txn.get("amt", None)
            try:
                amt = int(amt)
            except (ValueError, TypeError):
                amt = 0
            txn["amt_int"] = amt / 100000000

            mts_add = txn.get("mtsAdd", 0)
            try:
                mts_add = int(mts_add)
            except (ValueError, TypeError):
                mts_add = 0

            mts_mod = txn.get("mtsMod", 0)
            try:
                mts_mod = int(mts_mod)
            except (ValueError, TypeError):
                mts_mod = 0

            txn["mtsAdd_hr"] = unix_to_human(mts_add)
            txn["mtsMod_hr"] = unix_to_human(mts_mod)

            writer.writerow(txn)

# Function to write holders to CSV
def write_holders_to_csv(filename, holders):
    filename = sanitize_filename(filename)
    fieldnames = ["address", "minted", "transferred", "calc_balance", "api_balance", "api_locked", "delta"]
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for address, data in holders.items():
            row = {
                "address": address,
                "minted": data["minted"],
                "transferred": data["transferred"],
                # "listed": data["listed"],                
                "calc_balance": data["balance"],
                "api_balance": data["api_balance"],
                "api_locked": data["api_locked"],
                "delta": data["delta"]
            }
            writer.writerow(row)
