import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests
from fastecdsa import keys,curve
import base58

class Blockchain(object):
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        self.wallets = set()

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash):

        block = {
            'index': len(self.chain) + 1,
            'timestamp': int(time()),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash,
        }

        self.current_transactions = []

        self.chain.append(block)

        return block

    def new_transactions(self, sender, recipient, amount, sign):

        if sender == "coinbase" or self.verify_priv_key(sign, sender):

            transaction = {
                    'vin': [
                        {
                            'sender': sender,
                            'recipient': recipient,
                        }
                    ],
                    'vout': [
                        {
                            'value': amount,
                        },
                        {
                            'value': self.check_saldo(sender) - amount
                        }
                    ]
                }

            if sender == "coinbase": #mined coins
                self.current_transactions.append(transaction)
                return transaction
            elif transaction["vout"][1]["value"] < 0: #if sender doesnt have enough coins to pay
                return False
            else:
                self.current_transactions.append(transaction)
                return transaction
        else:
            return False

    @property
    def return_last_block(self):

        return self.chain[-1]

    def proof_of_work(self, last_block):

        previous_proof = last_block['proof']
        previous_hash = last_block['previous_hash']
        proof = 0

        while self.validate_proof(proof, previous_proof, previous_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def validate_proof(proof, previous_proof, previous_hash):

        proof_formula = f'{previous_proof}{proof}{previous_hash}'.encode()
        proof_formula_hash = hashlib.sha256(proof_formula).hexdigest()
        return proof_formula_hash[:4] == '0000'

    @staticmethod
    def hash(block):

        block_string = json.dumps(block, sort_keys=True).encode()
        block_hash = hashlib.sha256(block_string).hexdigest()
        return block_hash

    def register_node(self, node_address):

        parsed_url = urlparse(node_address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def validate_chain(self, chain):

        current_index = 1

        while current_index < len(chain):

            block = chain[current_index]
            previous_block = chain[current_index - 1]

            print(f'{block}')
            print(f'{previous_block}')
            print("\n-----------\n")

            if block['previous_hash'] != self.hash(previous_block):
                return False

            if not self.validate_proof(block['proof'], previous_block['proof'], previous_block['previous_hash']):
                return False

            current_index += 1

        return True

    def resolve_conflicts(self):

        main_length = len(self.chain)
        new_chain = None

        neighbours = self.nodes

        for node in neighbours:
            print(f'{node}')
            try:
                response = requests.get(f'http://{node}/chain', timeout=3)
            except requests.exceptions.Timeout:
                print(f'Timeout in chain requests - {node}')
                continue

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > main_length and self.validate_chain(chain):
                    main_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def check_saldo(self, wallet_address):
        """
        Check specific wallet saldo by search all transactions in blockchain
        :param wallet_address: base58check encoded public key
        :return: Saldo of wallet_address (type - int)
        """

        current_index = 0
        chain = self.chain
        saldo = 0

        while current_index < len(chain):
            block = chain[current_index]
            transactions_length = len(block["transactions"])
            wallet_out_transaction = []
            wallet_in_transaction = []
            for i in range(0, transactions_length): #outcoming transactions
                if block["transactions"][i]["vin"][0]["sender"] == f"{wallet_address}":
                    wallet_out_transaction += block["transactions"][i]["vout"]

            wallet_out_transaction = wallet_out_transaction[::2] #every second vout value is out/incoming amount

            for d in wallet_out_transaction:
                saldo = saldo - (d['value'])

            for i in range(0, transactions_length): #incoming transactions
                if block["transactions"][i]["vin"][0]["recipient"] == f"{wallet_address}":
                    wallet_in_transaction += block["transactions"][i]["vout"]

            wallet_in_transaction = wallet_in_transaction[::2]

            for d in wallet_in_transaction:
                saldo = saldo + (d['value'])

            current_index += 1

        return saldo

    def show_transactions(self, wallet_address):
        """
        Check transactions corresponding with wallet_address
        :param wallet_address: base58check encoded public key
        :return: Transactions corresponding with address (type - tab)
        """

        current_index = 0
        chain = self.chain
        wallet_transactions = []

        while current_index < len(chain):
            block = chain[current_index]
            transactions_length = len(block["transactions"])
            for i in range(0, transactions_length):
                if block["transactions"][i]["vin"][0]["sender"] == f"{wallet_address}" or block["transactions"][i]["vin"][0]["recipient"] == f"{wallet_address}":
                    wallet_transactions.append(block["transactions"][i])

            current_index += 1

        return wallet_transactions

    @staticmethod
    def generate_wallet():
        """
        Generate wallet key pair and encode public_key to base58check format
        :return: Accurately function returns private_key corresponded with wallet_address
        """
        ###256b Private key generation
        priv_key = keys.gen_private_key(curve.P256)
        ###Change private key to hex
        priv_key_hex = hex(priv_key)
        ###Change private key from hex to dec
        #priv_key_from_hex = int(f"{priv_key_hex}", 16)

        # Get public key from private key as point
        pub_key = keys.get_public_key(priv_key, curve.P256)

        # Public key (K) as 128bit string str(x)+str(y)
        pub_key_128 = f"{format(pub_key.x, 'x')}" + f"{format(pub_key.y, 'x')}"

        # SHA256(K) - binary
        pub_key_hash_bin = hashlib.sha256(pub_key_128.encode()).digest()

        # RIPEMD160(SHA256(K))
        pub_key_hash_ripemd = hashlib.new('ripemd160', pub_key_hash_bin).digest()

        # Base58Check address
        pub_key_base58 = base58.b58encode_check(pub_key_hash_ripemd)

        # Add 'B' as network sign
        wallet_address = "B"+str(pub_key_base58)

        key_pair = [wallet_address, priv_key_hex]

        return key_pair

    def verify_priv_key(self, priv_key_hex, wallet_address):
        """
        Verify private_key compatibility with public_key result
        :param priv_key_hex: Private key written as hex
        :param wallet_address: base58check encoded public key
        :return: True if keys are compatible or False if not
        """
        # Convert hex priv_key to dec
        priv_key = int(f"{priv_key_hex}", 16)

        # Convert pub_key_base58 to ripemd160 bin
        pub_key_hash_ripemd1 = base58.b58decode_check(wallet_address[1:])

        # Get public key from private key as point
        pub_key = keys.get_public_key(priv_key, curve.P256)

        # Public key (K) as 128bit string str(x)+str(y)
        pub_key_128 = f"{format(pub_key.x, 'x')}" + f"{format(pub_key.y, 'x')}"

        # SHA256(K) - binary
        pub_key_hash_bin = hashlib.sha256(pub_key_128.encode()).digest()

        # RIPEMD160(SHA256(K))
        pub_key_hash_ripemd2 = hashlib.new('ripemd160', pub_key_hash_bin).digest()

        return pub_key_hash_ripemd1 == pub_key_hash_ripemd2

    def spread_transaction_post(self, transaction_dict):
        """
        Spread transaction to every node - make a post request to every compute node
        :param transaction_dict: Transaction returned by new_transaction() function (type - dict)
        :return: Nothing
        """

        neighbours = self.nodes
        for node in neighbours:
            print(f'{node}')
            try:
                response = requests.post(f'http://{node}/transaction/spread', json=transaction_dict, timeout=3)
                print("ODP")
                print(response.text)
            except requests.exceptions.Timeout:
                print(f'Timeout in chain requests - {node}')
                continue

    def spread_transaction(self, transaction_dict):
        """
        Spread transaction to current_transactions table on specific node
        :param transaction_dict: Transaction relayed as POST request parameter (type - dict)
        :return: Transactions list waiting for being mined on specific node
        """
        self.current_transactions.append(json.loads(transaction_dict))

        return self.current_transactions

