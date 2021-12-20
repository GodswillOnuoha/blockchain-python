"""Saves and Loads blockchain to and from a file"""

import json
import pickle

from collections import OrderedDict
from blockchain.block import Block
from blockchain.transaction import Transaction


FILE_NAME = "blockchain.txt"

# Save and load data using pickle
def load_data_pickle():
    with open(FILE_NAME, "rb") as f:
        file_content = pickle.loads(f.read())
        blockchain = file_content["chain"]
        open_transactions = file_content["open_transactions"]
    return blockchain, open_transactions


def save_data_pickle(blockchain, open_transactions):
    with open(FILE_NAME, "wb") as f:
        data = {"chain": blockchain, "open_transactions": open_transactions}
        f.write(pickle.dumps(data))


# Save and load data using json (To be used for development to view data)
def load_data_json():
    with open(FILE_NAME, "r") as f:
        file_content = f.readlines()

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

        return blockchain, open_transactions


def save_data_json(blockchain, open_transactions):
    hashable_chain = [
        block.__dict__
        for block in [
            Block(
                blk.index,
                blk.previous_hash,
                [tx.__dict__ for tx in blk.transactions],
                blk.proof,
                blk.timestamp
            )
            for blk in blockchain
        ]
    ]
    hashable_tx = [tx.__dict__ for tx in open_transactions]
    with open(FILE_NAME, "w") as f:
        f.write(json.dumps(hashable_chain))
        f.write("\n")
        f.write(json.dumps(hashable_tx))


# Save and load data interface
def save_data(blockchain, open_transactions):
    # save_data_pickle(blockchain, open_transactions)
    save_data_json(blockchain, open_transactions)


def load_data():
    # return load_data_pickle()
    return load_data_json()
