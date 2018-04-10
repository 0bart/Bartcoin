from flask import Flask, jsonify, request
from blockchain import Blockchain
from argparse import ArgumentParser
import json

# Instantiate the Node
app = Flask(__name__)

# Instantiate the Blockchain
blockchain = Blockchain()

# Generate a globally unique address for this node
node_identifier = blockchain.generate_wallet()
print(node_identifier); node_identifier=node_identifier[0]


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.return_last_block
    proof = blockchain.proof_of_work(last_block)

    blockchain.new_transactions(sender="coinbase", recipient=node_identifier, amount=1, sign=0)

    previous_hash = blockchain.hash(last_block)

    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def chain():

    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return jsonify(response), 200

@app.route('/transaction/new', methods=['POST'])
def transaction():

    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return "Missing values in transaction", 400

    transaction = blockchain.new_transactions(values['sender'], values['recipient'], values['amount'], values['sign'])
    index = blockchain.return_last_block["index"]
    if transaction:
        response = {
            'message': f'Transactions will be added in Block {index}'
        }
        blockchain.spread_transaction_post(json.dumps(transaction))
    else:
        response = {
            'message': f'Transaction unauthorized, not enough coins or bad sign!'
        }

    return jsonify(response), 201

@app.route('/transaction/spread', methods=['POST'])
def transaction_spread():
    transaction = request.get_json()
    transactions = blockchain.spread_transaction(transaction)
    response = {
        "Current transactions": f'{transactions}'
    }

    return jsonify(response), 201


@app.route('/nodes/register', methods=['POST'])
def register_node():

    values = request.get_json()

    nodes = values.get('nodes')
    required = ['nodes']
    if not all(k in values for k in required):
        return "Missing address", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': "New node have been added",
        'added_nodes': nodes,
        'total_nodes': list(blockchain.nodes),
    }

    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():

    changed = blockchain.resolve_conflicts()

    if changed:
        response = {
            'message': "Our chain was replaced",
            'new_chain': blockchain.chain,
        }
    else:
        response = {
            'message': "Our chain is authorative",
            'chain': blockchain.chain,
        }

    return jsonify(response), 200

@app.route('/wallet/transactions/<wallet_address>', methods=['GET'])
def show_transactions(wallet_address):
#    blockchain.resolve_conflicts()

    wallet_transactions = blockchain.show_transactions(wallet_address)

    response = {
        "wallet_address": wallet_address,
        "transactions": wallet_transactions,
    }

    return jsonify(response), 200

@app.route('/wallet/saldo/<wallet_address>', methods=['GET'])
def show_saldo(wallet_address):
    saldo = blockchain.check_saldo(wallet_address)

    response = {
        'wallet_address': wallet_address,
        'saldo': saldo
    }

    return jsonify(response), 200

@app.route('/wallet/generate', methods=['GET'])
def generate_wallet():
    key_pair = blockchain.generate_wallet()
    wallet_address = key_pair[0]
    priv_key = key_pair[1]
    blockchain.wallets.add(wallet_address)

    response = {
        "message": "Hide your priv key, dont show it to anyone",
        "wallet_address": wallet_address,
        "private_key": priv_key,
    }

    return jsonify(response), 200


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)