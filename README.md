# air-wallet

a simple bitcoin wallet for self-custody (with basic ethereum wallet support as well)

the emphasis is on ease of recovery so you can set and forget your bitcoin in cold storage and feel confident that the private keys are both secure (no one can steal them) and safe (the rightful owner can reconstruct them)

ABSOLUTELY NO WARRANTY DO YOUR OWN DUE DILLIGENCE

## requirements and installation

Requires: node 10+, python 3.6+

Installation Steps:

1. clone repo, enter root directory
2. yarn install
3. pip3 install python-bitcoinlib cryptography ecdsa cryptos requests cryptocompare

Note: relies on a number of external apis under the hood which could disappear or change in the long run. blockchain.info, blockcypher.com, mempool.space, cryptocompare.com are the apis to verify are still in existence if you are getting any errors or unknown behavior (especially if it has been a long time since this repo was updated). However broken external api calls will never comrpomise wallet security or your ability to recover the wallet, they only fetch public data.

## setup
To set up your wallet you need to chose a strong, long mnemonic passphrase and then encrypt this menmonic to create the airwallet key file.

`python3 scripts/fernetAES.py encrypt path/to/output/keyfile`

First enter a long mnemonic seed phrase with good entropy, preferrably one that you also memorize (or back up on paper somewhere very secure). Then enter a password that will decrypt this file containing the mnemonic. The process will store a keyfile at the specified path.

After creation try:

`python3 scripts/fernetAES.py decrypt path/to/encrypted/keyfile`

Make absolutely certain you can decrypt the keyfile with the password. Do this in a trusted offline environment wherever possible. Be certain you know your password and you have the keyfile backed up. Memorize or securely back up your mnemonic as well if you want to be fully certain you can reconstruct your keys even in a worst case scenario (lost the keyfile or forgot the password). 

Nice thing about encrypted keyfile + password is you can back up encrypted keyfile on the cloud if you have a strong password so you can easily download your wallet to any machine (clone this repo, download your keyfile and you are good to go). The last resort is the underlying mnemonic phrase and the salting scheme. If you lose everything but you know the mnemonic and salting scheme you can recover the private keys directly from warpwallet algorithm.

## use
To interact with a single keypair in the wallet run e.g.

`python3 airwallet.py path/to/encrypted/keyfile btc 0 0 <command>`

addresses are indexed by two numbers 0-9 giving each air wallet only 100 addresses. This is on purpose to make manual tracking and accounting for the addresses in the wallet as simple and foolproof as possible. If you know your mnemonic and understand the simple priciples of the airwallet you can manually reconstruct all your addresses and private keys quite easily, even in the case that all the accompanying software is lost.

Commands are:

- `address` see the public address
- `balance` see the balance in BTC and USD of the address 
- `export` see the private key of the address (not recommended unless you know why)
- `send` create a P2PKH transaction spending from the address (to a specified receiving address)
- `sweep` create a P2PKH transaction that 'sweeps' all the bitcoin from the address (to a specified receiving address)

Lastly to get a report on ALL 100 addresses in the wallet at once run:

`python3 airwallet.py path/to/encrypted/keyfile btc report`
