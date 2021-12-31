"""Saves and Loads blockchain to and from a file"""

import json
import pickle
import os

from dotenv import load_dotenv


from blockchain.block import Block
from blockchain.transaction import Transaction

load_dotenv()

f_env = os.getenv("FLASK_ENV")
FILE_NAME = f"{f_env}_blockchain.txt"
FILE_ENCODING = "utf-8"

# Save and load data using pickle
def load_data_pickle():
    """Loads file into python objects from pickle format file.

    Returns:
        b, o, p (tuple): A tuple of blockchain, open_transactions, peer_nodes as saved to file
    """
    with open(FILE_NAME, "rb") as file:
        file_content = pickle.loads(file.read())
        blockchain = file_content["chain"]
        open_transactions = file_content["open_transactions"]
        peer_nodes = file_content["peer_nodes"]
    return blockchain, open_transactions, peer_nodes


def save_data_pickle(blockchain, open_transactions, peer_nodes):
    """Saves given objects to a file in pickle format"""
    with open(FILE_NAME, "wb") as file:
        data = {
            "chain": blockchain,
            "open_transactions": open_transactions,
            "peer_nodes": peer_nodes,
        }
        file.write(pickle.dumps(data))


def load_data_json():
    """Loads file into python objects from json format file.

    Returns:
        b, o, p (tuple): A tuple of blockchain, open_transactions, peer_nodes as saved to file
    """
    with open(FILE_NAME, "r", encoding=FILE_ENCODING) as file:
        file_content = file.readlines()

        blockchain = json.loads(file_content[0][:-1])

        # convert to OrderedDict
        blockchain = [
            Block(
                index=block["index"],
                previous_hash=block["previous_hash"],
                transactions=[
                    Transaction(
                        tx["sender"], tx["recipient"], tx["amount"], tx["signature"]
                    )
                    for tx in block["transactions"]
                ],
                proof=block["proof"],
                timestamp=block["timestamp"],
            )
            for block in blockchain
        ]

        open_transactions = json.loads(file_content[1])
        # convert to OrderedDict
        open_transactions = [
            Transaction(tx["sender"], tx["recipient"], tx["amount"], tx["signature"])
            for tx in open_transactions
        ]
        peer_nodes = set(json.loads(file_content[2]))

        return blockchain, open_transactions, peer_nodes


def save_data_json(blockchain, open_transactions, peer_nodes):
    """Saves given objects to a file in json format"""
    saveable_chain = [
        block.__dict__
        for block in [
            Block(
                blk.index,
                blk.previous_hash,
                [tx.__dict__ for tx in blk.transactions],
                blk.proof,
                blk.timestamp,
            )
            for blk in blockchain
        ]
    ]
    saveable_tx = [tx.__dict__ for tx in open_transactions]
    with open(FILE_NAME, "w", encoding=FILE_ENCODING) as file:
        file.write(json.dumps(saveable_chain))
        file.write("\n")
        file.write(json.dumps(saveable_tx))
        file.write("\n")
        file.write(json.dumps(list(peer_nodes)))


# Save and load data interface
def save_data(blockchain, open_transactions, peer_nodes):
    """Saves Blockchain, open transactions and peer nodes to file"""
    # save_data_pickle(blockchain, open_transactions, peer_nodes)
    save_data_json(blockchain, open_transactions, peer_nodes)


def load_data():
    """Reads Blockchain, open transactions and peer nodes from file"""
    # return load_data_pickle()
    return load_data_json()
