"""Exposes block chain functions to remote nodes via Flask"""

from flask import Flask, jsonify, request
from flask_cors import CORS

from blockchain.wallet import Wallet
from blockchain.blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)

CORS(app)


@app.route("/balance", methods=["GET"])
def get_balance():
    """Returns node balance"""
    balance = blockchain.get_balance()
    if balance is None:
        response = {
            "message": "Loading balance failed.",
            "wallet_set_up": wallet.public_key is not None,
        }
        return jsonify(response), 400

    response = {"funds": balance, "message": "Fetched balance successfully"}
    return jsonify(response)


@app.route("/wallet", methods=["POST"])
def create_keys():
    """Returns a new set of created kyes"""
    wallet.creat_keys()

    if not wallet.save_keys():
        response = {"message": "Saving keys failed"}
        return jsonify(response), 500

    blockchain.update_id(wallet.public_key)
    response = {
        "public_key": wallet.public_key,
        "private_key": wallet.private_key,
        "funds": blockchain.get_balance(),
    }
    return jsonify(response), 201


@app.route("/wallet", methods=["GET"])
def load_keys():
    """Loads and returns existing key set"""
    if not wallet.load_keys():
        response = {"message": "Loading keys failed"}
        return jsonify(response), 500

    blockchain.update_id(wallet.public_key)
    response = {
        "public_key": wallet.public_key,
        "private_key": wallet.private_key,
        "funds": blockchain.get_balance(),
    }
    return jsonify(response)


@app.route("/chain", methods=["GET"])
def get_chain():
    """Returns blockchain"""
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_blk in dict_chain:
        dict_blk["transactions"] = [tx.__dict__ for tx in dict_blk["transactions"]]

    return jsonify(dict_chain)


@app.route("/nodes", methods=["POST"])
def add_node():
    """Adds a peer node"""
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
    """Removes a peer node"""
    if node_url == "" or node_url is None:
        response = {"message": "No node found."}
        return jsonify(response), 400

    blockchain.remove_node(node_url)
    response = {"message": "Node successfully removed", "nodes": blockchain.get_nodes()}
    return jsonify(response)


@app.route("/nodes")
def get_nodes():
    """Returns a list of all peer nodes"""
    nodes = blockchain.get_nodes()
    response = {"message": "Nodes successfully fetched", "nodes": nodes}
    return jsonify(response)


@app.route("/transactions", methods=["GET"])
def get_open_transactions():
    """Returns a list of transactions that isn't added to the blockchain yet"""
    transactions = blockchain.get_open_transactions()
    dict_txs = [tx.__dict__ for tx in transactions]

    return jsonify(dict_txs)


@app.route("/transaction", methods=["POST"])
def add_transaction():
    """Adds a new transaction to open transactions"""
    if wallet.public_key is None:
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


@app.route("/broadcast-transaction", methods=["POST"])
def broadcast_transction():
    """Updates own copy of open transactions when a different node adds a new transaction"""
    values = request.get_json()

    if not values:
        response = {"message": "No data found."}
        return jsonify(response), 400

    required_fields = ["sender", "recipient", "amount", "signature"]
    if not all(field in values for field in required_fields):
        response = {"message": "Required field missing."}
        return jsonify(response), 400

    success = blockchain.add_transaction(
        values["recipient"],
        values["sender"],
        values["signature"],
        values["amount"],
        is_broadcast=True,
    )
    if not success:
        response = {"message": "Validation failed"}
        return jsonify(response), 500

    response = {"message": "transacttion validated"}
    return jsonify(response), 200


@app.route("/broadcast-block", methods=["POST"])
def broadcast_block():
    """Updates local chain when a different node mines a new block"""
    values = request.get_json()
    if not values or not "block" in values:
        response = {"message": "Required field missing"}
        return jsonify(response), 400
    block = values["block"]
    if block["index"] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {"message": "Block accepted"}
            return jsonify(response), 200
        else:
            response = {"message": "Block seems invalid"}
            return jsonify(response), 409
    elif block["index"] > blockchain.chain[-1].index:
        blockchain.resolve_conflicts = True
        response = {"message": "Blockchain seems to differ fom local chain"}
        return jsonify(response), 200
    else:
        response = {"message": "shorter blockchain, block not added"}
        return jsonify(response), 409


@app.route("/mine", methods=["POST"])
def mine_blocks():
    """Confirms open transactions and adds a new block to chain"""
    if blockchain.resolve_conflicts:
        response = {"message": "Block not added, resolve conflicts first"}
        return jsonify(response), 409
    block = blockchain.mine_block()

    if block is not None:
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
        "wallet_set_up": wallet.public_key is not None,
    }
    return jsonify(response), 500


@app.route("/resolve-conflicts", methods=["POST"])
def resolve_conflicts():
    """Resolve conflicts in chain blocks"""
    replaced = blockchain.resolve_conflict()
    if replaced:
        response = {"message": "Chain replaced"}
    else:
        response = {"message": "Local chain retained"}
    return jsonify(response), 200


class Node:
    """Provides a run method for starting the node"""

    def start(self, host="0.0.0.0", port="3000"):
        """Starts a node instance

        Arguments:
            host: The interface to expose app
            port: The port to expose app
        """
        app.run(host=host, port=port)
