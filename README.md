# air-wallet

an extremely simple bitcoin wallet for self-custody. 

the emphasis is on ease of recovery so you can set and forget your bitcoin in cold storage and feel confident that the keys are both secure (no one can steal the private keys) and safe (the rightful owner can still reconstruct the private keys)

# setup
To generate an encrpyted keyfile run:

`python3 scripts/fernetAES.py encrypt path/to/output/file`

enter a long mnemonic seed phrase with good entropy, preferrably one that you also memorize (but strength is most important - DO NOT pick a simple mnemonic)

enter a passphrase that will decrypt the file containing the mnemonic (this should also be strong, but you MUST remember this one)

after creation try

`python3 scripts/fernetAES.py decrypt path/to/encrypted/keyfile`

to make sure you can decrypt the keyfile with the password.

# use
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