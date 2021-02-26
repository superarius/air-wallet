# air-wallet

an extremely simple bitcoin wallet for self-custody. 

the emphasis is on ease of recovery so you can set and forget your bitcoin in cold storage and feel confident that the private keys are both secure (no one can steal them) and safe (the rightful owner can reconstruct them)

# setup
To set up your wallet you need to chose a strong, long mnemonic passphrase and then encrypt this menmonic to create the airwallet key file.

`python3 scripts/fernetAES.py encrypt path/to/output/keyfile`

First enter a long mnemonic seed phrase with good entropy, preferrably one that you also memorize. Then enter a password that will decrypt this file containing the mnemonic. The process will store a keyfile at the specified path.

After creation try:

`python3 scripts/fernetAES.py decrypt path/to/encrypted/keyfile`

Make absolutely certain you can decrypt the keyfile with the password. Do this in a trusted offline environment wherever possible. Be certain you know your password and you have the keyfile backed up. Memorize your mnemonic as well  if you want to be fully certain you can reconstruct your keys even in a worst case scenario (lost the keyfile, forgot the password)

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
