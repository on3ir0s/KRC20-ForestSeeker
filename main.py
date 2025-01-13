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


import asyncio
import os
from transaction_retrieval import retrieve_transactions, retrieve_all_transactions, retrieve_transactions_from_file
from balance_computation import calculate_balance, process_holders_snapshot

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
    output_dir = os.path.join(script_dir, "files_io")  # Create the "files_io" directory path
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist    
    os.chdir(output_dir)  # Set "files_io" as the current working directory     
    
    while True:
        try:
            print("KRC20 Forest Seeker")
            print("v0.1 - (c) 2025 on3ir0s\n")
            print("\nA. TRANSACTIONS RETRIEVAL")
            print("SINGLE TICKER")
            print("1) Retrieve transactions file for a wallet and a KRC20 ticker")
            print("2) Retrieve multiple transactions files for a batch of wallets and a KRC20 ticker")
            print("3) Retrieve full transactions file for a KRC20 ticker (SNAPSHOT input file)")
            print("ALL TICKERS")
            print("4) Retrieve transactions file for a wallet and all KRC20 tickers")
            print("\nB. BALANCES CALCULATION")
            print("SINGLE TICKER")
            print("5) Calculate balance for a wallet and a KRC20 ticker from a transactions file")
            print("6) Compute balance SNAPSHOT file for a KRC20 ticker from a full transactions file")
            print("7) Compute balance SNAPSHOT file at a specific opscore for a KRC20 ticker from a full transactions file")
            # print("\nC. TRANSACTIONS MAPPING")
            # print("*** Coming soon**")
            print("\nC. OTHER")
            print("x) Exit")
            choice = input("\nChoose an option: ")

            if choice == "1":
                address = ''
                while "kaspa:" not in address:
                    address = input("Enter Kaspa wallet: ").lower()
                tick = ''
                while not (4 <= len(tick) <= 6):
                    tick = input("Enter ticker: ").lower()
                asyncio.run(retrieve_transactions(address, tick))
                input("Press ENTER to continue.\n")

            elif choice == "2":
                filename = input("Enter the filename of the addresses file: ").lower()
                tick = filename.split('_')[1].lower()
                while not (4 <= len(tick) <= 6):
                    tick = input("Enter ticker: ").lower()
                asyncio.run(retrieve_transactions_from_file(filename, tick))
                input("Press ENTER to continue.\n")
                     
            elif choice == "3":
                tick = ''
                while not (4 <= len(tick) <= 6):
                    tick = input("Enter ticker: ").lower()
                asyncio.run(retrieve_all_transactions(tick))
                input("Press ENTER to continue.\n")
            
            elif choice == "4":
                address = ''
                while "kaspa:" not in address:
                    address = input("Enter Kaspa wallet: ").lower()
                asyncio.run(retrieve_transactions(address))
                input("Press ENTER to continue.\n")
            
            elif choice == "5":
                filename = input("Enter the filename of the transaction file: ").lower()
                tick = filename.split('_')[1].lower()
                while not (4 <= len(tick) <= 6):
                    tick = input("Enter ticker: ").lower()
                addr_token = filename.split('_')[-1].split('.')[0]
                address = f"kaspa:{addr_token}".lower()
                calculate_balance(filename, address, tick)
                input("Press ENTER to continue.\n")
            
            elif choice == "6":
                filename = input("Enter the filename of the full transaction file: ")
                tick = filename.split('_')[1].lower()
                while not (4 <= len(tick) <= 6):
                    tick = input("Enter ticker: ").lower()
                process_holders_snapshot(filename, tick, mode="end")
                input("Press ENTER to continue.\n")
            
            elif choice == "7":
                filename = input("Enter the filename of the full transaction file: ")
                tick = filename.split('_')[1].lower()
                while not (4 <= len(tick) <= 6):
                    tick = input("Enter ticker: ").lower()
                opscore = -1
                while opscore <= 0:                 
                    try:
                        opscore = int(input("Enter the opscore: "))
                    except ValueError:
                        pass
                process_holders_snapshot(filename, tick, opscore=opscore, mode="opscore")
                input("Press ENTER to continue.\n")
            elif choice == "x":
                break
            else:
                input("Option not implemented. Press ENTER to continue.\n")
        except:
            input("\nAn error occurred. Press ENTER to continue.\n")

if __name__ == "__main__":
    main()
