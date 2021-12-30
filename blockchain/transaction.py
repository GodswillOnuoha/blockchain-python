"""Exposes a transaction class"""

from collections import OrderedDict


class Transaction:
    """A transaction which can be added to a block in the blockchain.

    Attributes:
        sender: The sender of the coins.
        recipient: The recipient of the coins.
        amount: The amount of coins sent
        signature: The signatureof the transaction.
    """

    def __init__(self, sender, recipient, amount, signature):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_ordered_dict(self):
        """Returns an ordered dict of transaction"""
        return OrderedDict(
            [
                ("sender", self.sender),
                ("recipient", self.recipient),
                ("amount", self.amount),
                ("signature", self.signature),
            ]
        )
