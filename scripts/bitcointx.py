
'''
Hyper simple helper tool for spending from a bitcoin paper wallet
IMPORTANT: only supports P2PKH transactions (send/receive to bitcoin addresses that start with a "1")

implemented by: superarius
see MIT License in root directory of https://github.com/superarius/paper-wallet-tx
'''

import hashlib, binascii, requests, time, ecdsa, sys, getpass
from cryptos import b58check_to_hex
from ecdsa import SigningKey, SECP256k1

from bitcoin import SelectParams
from bitcoin.core import b2x, lx, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, COIN
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret, P2PKHBitcoinAddress

def simple_transaction(sender_priv, receiver_address, amount_btc, testnet=False, change_address=None, fee_type='standard', sat_per_byte=None):
	amount = int(amount_btc*COIN)
	secret = CBitcoinSecret(sender_priv)
	sender = f"{P2PKHBitcoinAddress.from_pubkey(secret.pub)}"
	utxos = get_unspent(sender, testnet=testnet)
	if sat_per_byte == None:
		sat_per_byte = get_current_fee(type_=fee_type)
	gross_input_thresh = amount+int(78*sat_per_byte)
	inputs = []
	total = 0
	for utxo in utxos:
		total += utxo["value"]
		inputs.append(utxo)
		gross_input_thresh += int(181*sat_per_byte)
		if total >= gross_input_thresh:
			break
	est_size = (181*len(inputs))+68+10
	sat_fee = int(sat_per_byte*est_size)
	if change_address == None:
		change_address = sender
	if amount+sat_fee > total:
		raise ValueError("Not enough fund for transaction (and fee)")
	unsigned = unsigned_transaction(inputs, [{"value": amount, "address": receiver_address}], sat_fee, change_address, testnet=testnet)
	return sign_tx(sender_priv, unsigned)

def simple_send_all(sender_priv, receiver_address, testnet=False, fee_type='standard', sat_per_byte=None):
	secret = CBitcoinSecret(sender_priv)
	sender = f"{P2PKHBitcoinAddress.from_pubkey(secret.pub)}"
	utxos = get_unspent(sender, testnet=testnet)
	if (len(utxos)==0):
		raise ValueError('nothing to send')
	inputs = []
	total = 0
	for utxo in utxos:
		total += utxo["value"]
		inputs.append(utxo)
	if sat_per_byte == None:
		sat_per_byte = get_current_fee(type_=fee_type)
	est_size = (181*len(inputs))+68+10
	sat_fee = int(sat_per_byte*est_size)
	amount = total-sat_fee
	unsigned = unsigned_transaction(inputs, [{"value": amount, "address": receiver_address}], sat_fee, sender, testnet=testnet)
	return sign_tx(sender_priv, unsigned)

def unsigned_transaction(inputs, outputs, satoshi_fee, change_address, testnet=False):
	"""
	Generate the **unsigned** transaction hex code
	:param inputs: a list of utxos [{"value": value, "index": index, "txid":txid}]
	:param outputs: [{"address": address, "value" : value},...]
	:param satoshi_fee: transaction fee in satoshi
	:param change_address: remaining change return address
	:param testnet: flag to enable/disable mainnet vs testnet
	:return: unsigned transaction hex
	"""
	if testnet:
		SelectParams('testnet')
	else:
		SelectParams('mainnet')
	gross_input_thresh = sum(i['value'] for i in outputs) + satoshi_fee
	gross_input = sum(i['value'] for i in inputs)
	if gross_input == gross_input_thresh:
		pass
	elif gross_input > gross_input_thresh:
		outputs.append({'value': gross_input - gross_input_thresh, 'address': change_address})
	else:
		raise ValueError("Not enough bitcoin inputs for such a transaction")
	tx_inputs = [create_transaction_input(i) for i in inputs]
	tx_outputs = [create_transaction_output(i) for i in outputs]
	tx = CMutableTransaction(tx_inputs, tx_outputs)
	return b2x(tx.serialize())

def sign_tx(private_key, hex_data):
	'''
	sign transaction inputs with private key (assumes this key unlocks all inputs)
	:param private_key: WIF base58 private key
	:param hex_data: unsigned transaction hex
	:return: signed transaction hex
	'''
	secret = CBitcoinSecret(private_key)
	pubkey = binascii.hexlify(secret.pub).decode('utf-8')
	public_address = f"{P2PKHBitcoinAddress.from_pubkey(secret.pub)}"
	split_data = hex_data.split("00ffffffff")
	input_stubs = split_data[:-1]
	output_stub = split_data[-1]
	pre_sig_script = '1976a914'+b58check_to_hex(public_address)+'88acffffffff'
	sig_stubs = []
	for i in range(len(input_stubs)):
		signing_message = ''
		for j in range(i):
			signing_message += input_stubs[j]+'00ffffffff'
		signing_message += input_stubs[i] + pre_sig_script
		for k in range(i+1, len(input_stubs)):
			signing_message += input_stubs[k]+'00ffffffff'
		signing_message += output_stub+'01000000'
		hashed_message = hashlib.sha256(hashlib.sha256(bytes.fromhex(signing_message)).digest()).digest()
		signingkey = ecdsa.SigningKey.from_string(bytes.fromhex(b58check_to_hex(private_key)), curve=ecdsa.SECP256k1)
		SIG = binascii.hexlify(signingkey.sign_digest(hashed_message, sigencode=ecdsa.util.sigencode_der_canonize)).decode('utf-8')
		siglen = len(SIG+'01')/2
		publen = len(pubkey)/2
		if siglen%1==0 and publen%1==0:
			siglen = hex(int(siglen))[2:]
			publen = hex(int(publen))[2:]
			if len(publen)%2 != 0 or len(siglen)%2 != 0:
				raise ValueError('issue parsing scriptsig')
		else:
			raise ValueError('issue parsing scriptsig')
		ScriptSig = siglen + SIG + '01' + publen + pubkey
		scriptlen = len(ScriptSig)/2
		if scriptlen%1==0:
			scriptlen=hex(int(scriptlen))[2:]
		if len(scriptlen)%2 != 0:
			raise ValueError('issue parsing scriptsig')
		sig_stub = scriptlen+ScriptSig+'ffffffff'
		sig_stubs.append(sig_stub)
	bytes_ = ''
	for q in range(len(sig_stubs)):
		bytes_ += input_stubs[q]+sig_stubs[q]
	bytes_ += output_stub
	return bytes_

def create_transaction_input(input_):
	"""
	transform the unsigned transaction input
	:param input_: unsigned transaction input
	:return: input formatted as transaction hex code
	"""
	return CMutableTxIn(COutPoint(lx(input_['txid']), input_['index']))

def create_transaction_output(output_):
	"""
	transform the transaction output into hex code
	:param output__: unsigned transaction output
	:return: output formatted as transaction hex code
	"""
	return CMutableTxOut(output_['value'], CBitcoinAddress(output_['address']).to_scriptPubKey())

def get_unspent(address, testnet=False):
	"""
	Get the unspent transaction outputs for a bitcoin address
	:param address: address to be checked
	:param testnet: flag to set mainnet vs testnet
	:return: [
		{
			"value" : amount_of_unspent_satoshis,
			"index" : index_of_previous_transaction,
			"txid"  : previous_tracsaction_id,
		}
	]
	"""
	network = 'test3' if testnet else 'main'
	req = f'https://api.blockcypher.com/v1/btc/{network}/addrs/{address}'
	try:
		resp = requests.get(req, params={"unspentOnly":"true"})
		response = resp.json()
	except:
		time.sleep(2)
		response = requests.get(req, params={"unspentOnly":"true"}).json()
	try:
		utxos = response['txrefs']
	except:
		utxos = []
	clean_utxos = [{'value': i['value'], 'index': i['tx_output_n'], 'txid': i['tx_hash']} for i in utxos]
	return clean_utxos

def get_current_fee(type_='standard'):
	'''
	Calculate transaction fees based on current network activity
	:param type_: specify the type of fee ('fast', 'standard', 'hour', 'cheap')
	'''
	if type_ == 'cheap':
		req = "https://api.blockcypher.com/v1/btc/main"
		try:
			resp = requests.get(req)
			response = resp.json()
		except:
			time.sleep(2)
			resp = requests.get(req)
			response = resp.json()
		return int(response['medium_fee_per_kb']/1000)
	else:
		req = "https://mempool.space/api/v1/fees/recommended"
		try:
			resp = requests.get(req)
			response = resp.json()
		except:
			time.sleep(2)
			resp = requests.get(req)
			response = resp.json()
		if type_ == 'fast':
			return int(response["fastestFee"])
		elif type_ == 'standard':
			return int(response["halfHourFee"])
		elif type_ == 'hour':
			return int(response["hourFee"])
		else:
			raise ValueError("Fee type %s not in ('fast', 'standard', 'hour', 'cheap')" % type_)


def push_transaction(transaction, testnet=False):
	"""
	Publish a transaction to the bitcoin blockchain
	:param transaction: hex string transaction code
	:param testnet: flag to set publish to mainnet vs testnet
	:return: the `https://chain.so/api/v2/send_tx/` json response
	"""
	data = {'tx_hex': transaction}
	network = 'BTCTEST' if testnet else 'BTC'
	response = requests.post(f'https://chain.so/api/v2/send_tx/{network}', data=data)
	return response.json()

if __name__ == '__main__':
	if len(sys.argv)<4:
		raise ValueError("")
	command, priv, recv_addr = sys.argv[1:4]
	if command == "sweep":
		print(simple_send_all(priv, recv_addr))
	elif command == "send":
		amount, change_addr = sys.argv[4:]
		print(simple_transaction(priv, recv_addr, float(amount), change_address=change_addr))
	else:
		raise ValueError("")

