from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.wrappers import response
import blockchain
from blockchain import block
from blockchain import transaction

from blockchain.wallet import Wallet
from blockchain.blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)

CORS(app)


@app.route("/")
def get_ui():
    return "this works"


@app.route("/balance", methods=["GET"])
def get_balance():
    balance = blockchain.get_balance()
    if balance == None:
        response = {
            "message": "Loading balance failed.",
            "wallet_set_up": wallet.public_key != None,
        }
        return jsonify(response), 400

    response = {"funds": balance, "message": "Fetched balance successfully"}
    return jsonify(response)


@app.route("/wallet", methods=["POST"])
def create_keys():
    wallet.creat_keys()

    if not wallet.save_keys():
        response = {"message": "Saving keys failed"}
        return jsonify(response), 500

    global blockchain
    blockchain = Blockchain(wallet.public_key)
    response = {
        "public_key": wallet.public_key,
        "private_key": wallet.private_key,
        "funds": blockchain.get_balance(),
    }
    return jsonify(response), 201


@app.route("/wallet", methods=["GET"])
def load_keys():
    if not wallet.load_keys():
        response = {"message": "Loading keys failed"}
        return jsonify(response), 500

    global blockchain
    blockchain = Blockchain(wallet.public_key)
    response = {
        "public_key": wallet.public_key,
        "private_key": wallet.private_key,
        "funds": blockchain.get_balance(),
    }
    return jsonify(response)


@app.route("/chain", methods=["GET"])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_blk in dict_chain:
        dict_blk["transactions"] = [tx.__dict__ for tx in dict_blk["transactions"]]

    return jsonify(dict_chain)


@app.route("/nodes", methods=["POST"])
def add_node():
    values = request.get_json()

    if not values:
        response = {"message": "No data found."}
        return jsonify(response), 400

    if not "node" in values:
        response = {"message": "Required field missing"}
        return jsonify(response), 400

    node = values["node"]
    blockchain.add_node(node)
    response = {"message": "Node successfully added", "nodes": blockchain.get_nodes()}
    return jsonify(response), 201


@app.route("/nodes/<node_url>", methods=["DELETE"])
def remove_node(node_url):
    if node_url == "" or node_url == None:
        response = {"message": "No node found."}
        return jsonify(response), 400

    blockchain.remove_node(node_url)
    response = {"message": "Node successfully removed", "nodes": blockchain.get_nodes()}
    return jsonify(response)


@app.route("/nodes")
def get_nodes():
    nodes = blockchain.get_nodes()
    response = {"message": "Nodes successfully fetched", "nodes": nodes}
    return jsonify(response)


@app.route("/transactions", methods=["GET"])
def get_open_transactions():
    transactions = blockchain.get_open_transactions()
    dict_txs = [tx.__dict__ for tx in transactions]

    return jsonify(dict_txs)


@app.route("/transaction", methods=["POST"])
def add_transaction():
    """Adds a new transaction"""
    if wallet.public_key == None:
        response = {"message": "No wallet set up."}
        return jsonify(response), 400

    values = request.get_json()
    if not values:
        response = {"message": "No data found"}
        return jsonify(response), 400

    required_fields = ["recipient", "amount"]
    if not all([field in values for field in required_fields]):
        response = {"message": "Required field missing."}
        return jsonify(response), 400

    recipient = values["recipient"]
    amount = values["amount"]
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(
        recipient, wallet.public_key, signature, amount
    )

    if not success:
        response = {"message": "Creating transaction failed"}
        return jsonify(response), 500

    response = {
        "message": "Transaction added successfully",
        "funds": blockchain.get_balance(),
        "transaction": {
            "sender": wallet.public_key,
            "recipient": recipient,
            "amount": amount,
            "signature": signature,
        },
    }
    return jsonify(response), 201


@app.route("/mine", methods=["POST"])
def mine_blocks():
    block = blockchain.mine_block()

    if block != None:
        dict_block = block.__dict__.copy()
        dict_block["transactions"] = [tx.__dict__ for tx in dict_block["transactions"]]
        response = {
            "message": "Block added succeffully",
            "block": dict_block,
            "funds": blockchain.get_balance(),
        }
        return jsonify(response), 201

    response = {
        "message": "Adding block failed",
        "wallet_set_up": wallet.public_key != None,
    }
    return jsonify(response), 500


class Node:
    def start(self, host="0.0.0.0", port="3000"):
        app.run(host=host, port=port)
