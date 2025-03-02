# README

# KRC20 Forest Seeker

## Description
A simple yet powerful command-line tool to retrieve Kaspa KRC20 transaction histories for individual wallets and entire tokens, and create snapshots of KRC20 token´s distribution at any point (opscore) in the past.

## Author
This software is brought to you by **on3ir0s** and the **Kastor´s $FOREST** team.
Visit [Kastor´s $FOREST profile on X](https://x.com/KastorsForest) and discover our world! 

If you like this work and you want to support its further development, please consider donating some $KAS or any KRC20 token to the following wallet: **kaspa:qpjt23hjcgsdmsq0zjtnswjrttdsk676qfm6p3r6ykn3e6yjtnw36ynyjve48**

## License
This project is open-source and licensed under the MIT License. 

## Functions
### TRANSACTIONS RETRIEVAL
SINGLE TICKER
- Retrieve transactions file for a wallet and a KRC20 ticker
- Retrieve multiple transactions files for a batch of wallets and a KRC20 ticker
- Retrieve full transactions file for a KRC20 ticker (SNAPSHOT input file)
<!-- -->
ALL TICKERS
- Retrieve transactions file for a wallet and all KRC20 tickers

### BALANCES CALCULATION (SHAPSHOT)
SINGLE TICKER
- Calculate balance for a wallet and a KRC20 ticker from a transactions file
- Compute balance SNAPSHOT file for a KRC20 ticker from a full transactions file
- Compute balance SNAPSHOT file at a specific opscore for a KRC20 ticker from a full transactions file")
<!-- -->

## Further Highlights:

### Safe

- No wallet connection required
- No seed phrase input required
- No private key input required
- No collection and sharing of Personally Identifiable Information (PII)
- Transaction history and snapshot computations based on wallets´ addresses and public data only

### Robust

- Designed to handle network disconnections and malformed server responses, ensuring reliable performance.

### Insightful

- Comprehensive KRC20 transaction history for one or multiple wallets
- Token distribution (snapshot) at any arbitrary time
- Distribution variations over time

...and further analytics you might not even have thought of yet!

## External dependencies
This software uses the public Kasplex APIs to retrieve the KRC20 transactions data. It does not rely on any other external data source.

## Use
### Prerequisites
- **python > 3.11**; testing has been performed with version **3.13.1**
- **git**, if the dedicated command will be used to clone the repo (see below)

### Creation of a virtual environment
It is recommended to use a virtual environment to manage dependencies. \
Create and activate one within a folder of your choice:
```sh
cd C:\[Folder]\[Of]\[Choice]
python -m venv venv
venv\Scripts\activate
```

### Download from GitHub
Download the project from GitHub, use the following command:
```sh
git clone https://github.com/on3ir0s/KRC20-ForestSeeker.git
```

### Installation of required modules
Install the required modules using pip:
```sh
pip install -r requirements.txt
```

### Launch
Launch the program from the command prompt:
```sh
python main.py
```

## Output

### The 'files_io' input-output folder
The input-output folder for all files read and generated by the program is called 'files_io' and it is located within the directory containing the file main.py. 

### Reading a snapshot_[tick]_[...].csv file
The snapshot .csv file for a token having ticker [tick], snapshot_[tick]_[...].csv, provides the following information:
- address: Kaspa address owning the token
- minted: amount of tokens minted by that address
- transferred: sum of all the tokens transferred to that address (positive numbers represent a total net inflow, negative numbers represent a total net outflow)
- calc_balance: address balance computed by the software based on all the individual transactions
- api_balance: address balance retrieved from the KASPLEX API
- api_locked: amount of currently listed tokens for that address retrieved from the KASPLEX API 
- delta: difference between the KASPLEX API data (balance and locked) and the calculated balance
This serves as:
- in 'full' mode, to double check to verify the correctness of the computed balance, as it should be 0 for all addresses; a limited number of exceptions might be present, due to the changes which might occur between the beginning of the transaction retrieval and the snapshot calculation
- in 'opscore' mode, to evaluate the change of tokens ownership between the current opscore and the user-defined one


