"""Exposes a block class"""

from time import time


class Block:
    """A single block in the chain

    Attributes:
        index: index of block in chain
        previous_hash: hash of previous block
        transactions: list of transactions added in block
        proof: proof of work
        timestamp: time
    """

    def __init__(self, index, previous_hash, transactions, proof, timestamp=time()):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.timestamp = timestamp
