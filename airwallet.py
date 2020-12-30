from subprocess import check_output
import os, sys, json
from getpass import getpass
import cryptocompare

BTC_SALT = 'btc'
ETH_SALT = 'eth'
WALLET_SIZE = 10
# operations on a single keypair inside wallet
BASIC_COMMANDS = ['address', 'sweep', 'send', 'export', 'balance']
# batch operations on all the keypairs inside wallet
WALLET_COMMANDS = ['report']

if __name__ == '__main__':
    try:
        if 6 != len(sys.argv) and 4 != len(sys.argv):
            print(f'error: malformatted arguments: path/to/keyfile [ { BTC_SALT } | {ETH_SALT} ] + idx_1 + idx_2 + [ {" | ".join(BASIC_COMMANDS)} ]')
            sys.exit(0)
        if 4 == len(sys.argv):
            filepath, base_salt, command = sys.argv[1:]
            if base_salt != BTC_SALT and base_salt != ETH_SALT:
                print(f'error: unrecognized base salt "{base_salt}" (options: {BTC_SALT} | {ETH_SALT})')
                sys.exit(0)
            if command not in WALLET_COMMANDS:
                print(f'error: unrecognized wallet batch command "{command}" (options: {" | ".join(WALLET_COMMANDS)})')
                sys.exit(0)
            currency = 'ethereum' if base_salt == ETH_SALT else 'bitcoin'
            if currency == 'ethereum':
                print(f'error: wallet report not yet implemented for ethereum')
                sys.exit(0)
            script_path = 'scripts/fernetAES.py'
            script_output = check_output([sys.executable, script_path, 'decrypt', filepath])
            base_mnemonic = script_output.decode().rstrip()
            print('be patient generating report can take a while...')
            totalBTC = 0
            totalUSD = 0
            USDbtc = cryptocompare.get_price('BTC', curr='USD')['BTC']['USD']
            for i in range(WALLET_SIZE):
                pwds = [(base_mnemonic+base_salt+str(i), base_salt+str(j)) for j in range(WALLET_SIZE)]
                script_path = 'scripts/getAddresses.js'
                script_output = check_output(['node', script_path, currency]+list(sum(pwds, ())))
                addresses = json.loads(script_output.decode().rstrip())
                script_path = 'scripts/btcbalance.py'
                script_output = check_output([sys.executable, 'scripts/btcbalance.py']+addresses)
                result = json.loads(script_output.decode().rstrip())
                for k, v in result.items():
                    vUSD = round(v*USDbtc, 2)
                    totalBTC += v
                    totalUSD += vUSD
                    print(f'{k}: {v} BTC ($ {vUSD})')
            print('----------------------')
            print(f'total: {totalBTC} BTC ($ {totalUSD})')
            sys.exit(0)
        else:
            filepath, base_salt, idx1, idx2, command = sys.argv[1:]
            if base_salt != BTC_SALT and base_salt != ETH_SALT:
                print(f'error: unrecognized base salt "{base_salt}" (options: {BTC_SALT} | {ETH_SALT})')
                sys.exit(0)
            if command not in BASIC_COMMANDS:
                print(f'error: unrecognized basic command "{command}" (options: {" | ".join(BASIC_COMMANDS)})')
                sys.exit(0)
            currency = 'ethereum' if base_salt == ETH_SALT else 'bitcoin'
            script_path = 'scripts/fernetAES.py'
            script_output = check_output([sys.executable, script_path, 'decrypt', filepath])
            base_mnemonic = script_output.decode().rstrip()
            pwd = base_mnemonic+base_salt+idx1
            salt = base_salt+idx2
            script_path = 'scripts/getWallet.js'
            script_output = check_output(['node', script_path, currency, pwd, salt])
            wallet_json = script_output.decode().rstrip()
            wallet = json.loads(wallet_json)
            if command == 'address':
                print(wallet["public"])
                sys.exit(0)
            elif command == 'export':
                input('are you sure you want to see private key ?? press ^C to abort (enter to continue)')
                print(wallet["private"])
                sys.exit(0)
            elif command == 'balance':
                script_path = 'scripts/btcbalance.py'
                script_output = check_output([sys.executable, 'scripts/btcbalance.py', wallet["public"]])
                result = json.loads(script_output.decode().rstrip())
                USDbtc = cryptocompare.get_price('BTC', curr='USD')['BTC']['USD']
                for k, v in result.items():
                    print(f'{k}: {v} BTC ($ {round(v*USDbtc, 2)})')
                sys.exit(0)
            elif command == 'send':
                print(f'retreived key for {wallet["public"]}')
                if currency == 'ethereum':
                    print('error: transactions not yet implemented for ethereum')
                    sys.exit(0)
                script_path = 'scripts/bitcointx.py'
                print("send from paper wallet (note: address reuse is not recommended)")
                recv_addr = input('receiver: ')
                if recv_addr[0] != "1":
                    print('error: receive address must begin with a 1')
                    sys.exit(0)
                amount = input('amount (BTC): ')
                change_addr = input("change address: ")
                if (change_addr == ""):
                    change_addr = wallet["public"]
                if change_addr[0] != "1":
                    print('error: change address must begin with a 1')
                    sys.exit(0)
                try:
                    script_output = check_output([sys.executable, script_path, command, wallet["private"], recv_addr, amount, change_addr])
                    print(script_output.decode().rstrip())
                except:
                    print('error: failed to generate transaction, are you sure you have enough funds?')
                    sys.exit(0)
            else:
                print(f'retreived key for {wallet["public"]}')
                if currency == 'ethereum':
                    print('error: transactions not yet implemented for ethereum')
                    sys.exit(0)
                script_path = 'scripts/bitcointx.py'
                print("sweep paper wallet")
                recv_addr = input('receiver: ')
                if recv_addr[0] != "1":
                    print('error: address must begin with a 1')
                    sys.exit(0)
                script_output = check_output([sys.executable, script_path, command, wallet["private"], recv_addr])
                if len(script_output.decode().rstrip()) < 90:
                    print('error: no btc in that address')
                    sys.exit(0)
                else:
                    print(script_output.decode().rstrip())
    except SystemExit:
        sys.exit(0)
    except:
        print('An unexpected error occured. Witholding error logging for security.')
        sys.exit(0)
