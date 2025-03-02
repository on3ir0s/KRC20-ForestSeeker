# Changelog

## 0.2 (2024-03-02)

### Implemented enhancements:
- added to the snapshot files the amount of listed ("locked") tokens provided by the Kasplex API, in addition to the current balance of each address
- added the date and retrieval time to the filename of all transactions file
- added the highest opScore taken into account to the filename of all snapshot files

### Fixed bugs:
- fixed the address balance calculations for single wallets and snapshots to correctly account for listed tokens
- fixed the calculation of the difference between the computed balances and the Kasplex API-retrieved balances ("delta"), which was inaccurate for a small number of wallets
- de-duplicated the retrieval of multiple transactions files from a batch of wallets when it includes repeated addresses


## 0.1 (2024-01-13)

Initial release

### Implemented functions:

#### TRANSACTIONS RETRIEVAL
SINGLE TICKER
- Retrieve transactions file for a wallet and a KRC20 ticker
- Retrieve multiple transactions files for a batch of wallets and a KRC20 ticker
- Retrieve full transactions file for a KRC20 ticker (SNAPSHOT input file)
<!-- -->
ALL TICKERS
- Retrieve transactions file for a wallet and all KRC20 tickers

#### BALANCES CALCULATION (SHAPSHOT)
SINGLE TICKER
- Calculate balance for a wallet and a KRC20 ticker from a transactions file
- Compute balance SNAPSHOT file for a KRC20 ticker from a full transactions file
- Compute balance SNAPSHOT file at a specific opscore for a KRC20 ticker from a full transactions file")
<!-- -->