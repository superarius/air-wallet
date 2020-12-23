from subprocess import check_output
import os, sys, json
from getpass import getpass

if __name__ == '__main__':
    try:
        if 6 != len(sys.argv):
            raise ValueError('')
        filepath, currency, x, y, command = sys.argv[1:]
        if currency != 'btc' and currency != 'eth':
            raise ValueError('')
        if command != 'address' and command != 'sweep' and command != 'send' and command != 'export':
            raise ValueError('')
        script_path = 'scripts/fernetAES.py'
        script_output = check_output([sys.executable, script_path, 'decrypt', filepath])
        base_mnemonic = script_output.decode().rstrip()
        pwd = base_mnemonic+currency+x
        salt = currency+y
        script_path = 'scripts/walletGenerator.js'
        script_output = check_output(['node', script_path, currency, pwd, salt])
        wallet_json = script_output.decode().rstrip()
        wallet = json.loads(wallet_json)
        if command == 'address':
            print(wallet["public"])
        elif command == 'export':
            input('are you sure you want to see private key ?? press ^C to abort')
            print(wallet["private"])
        elif command == 'send':
            print(f'retreived key for {wallet["public"]}')
            if currency == 'eth':
                print('transactions not yet implemented')
                raise ValueError('')
            script_path = 'scripts/bitcointx.py'
            print("send from paper wallet (note: address reuse is not recommended)")
            recv_addr = input('receiver: ')
            if recv_addr[0] != "1":
                print('address must begin with a 1')
                raise ValueError('')
            amount = input('amount (BTC): ')
            change_addr = input("change address: ")
            if (change_addr == ""):
                change_addr = wallet["public"]
            if change_addr[0] != "1":
                print('change address must begin with a 1')
                raise ValueError('')
            try:
                script_output = check_output([sys.executable, script_path, command, wallet["private"], recv_addr, amount, change_addr])
                print(script_output.decode().rstrip())
            except:
                print('error attempting transaction... are you sure you have enough funds?')
                raise ValueError('')
        else:
            print(f'retreived key for {wallet["public"]}')
            if currency == 'eth':
                print('transactions not yet implemented')
                raise ValueError('')
            script_path = 'scripts/bitcointx.py'
            print("sweep paper wallet")
            recv_addr = input('receiver: ')
            if recv_addr[0] != "1":
                print('address must begin with a 1')
                raise ValueError('')
            try:
                script_output = check_output([sys.executable, script_path, command, wallet["private"], recv_addr])
                if len(script_output.decode().rstrip()) < 90:
                    print('no btc in that address')
                else:
                    print(script_output.decode().rstrip())
            except:
                print('error attempting transaction... are you sure you have enough funds?')
                raise ValueError('')  
    except:
        print('ERROR - args should be: path/to/keyfile + [btc | eth] + idx_1 + idx_2 + [address | send | sweep]')
