import sys, re, json
from time import sleep
from urllib.request import urlopen

output = {}

def check_balance(address):
    global totbtc, totusd, output

    blockchain_tags_json = [ 
        'total_received',
        'final_balance',
        ]

    SATOSHIS_PER_BTC = 1e+8

    check_address = address

    parse_address_structure = re.match(r' *([a-zA-Z1-9]{1,34})', check_address)
    if ( parse_address_structure is not None ):
        check_address = parse_address_structure.group(1)
    else:
        return

    #Read info from Blockchain about the Address
    reading_state=1
    while (reading_state):
        try:
            htmlfile = urlopen("https://blockchain.info/address/%s?format=json" % check_address, timeout = 10)
            htmltext = htmlfile.read().decode('utf-8')
            reading_state  = 0
        except:
            sleep(60)

    blockchain_info_array = []
    tag = ''
    try:
        for tag in blockchain_tags_json:
            blockchain_info_array.append (
                float( re.search( r'%s":(\d+),' % tag, htmltext ).group(1) ) )
    except:
        return 

    for i, btc_tokens in enumerate(blockchain_info_array):
        if (blockchain_tags_json[i] == 'final_balance'): 
            btcs = btc_tokens/SATOSHIS_PER_BTC
            output[address] = btcs

if __name__ == '__main__':
    for address in sys.argv[1:]:
        check_balance(address)
    print(json.dumps(output))
