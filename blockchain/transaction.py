from collections import OrderedDict

from blockchain.utility.printable import Printable


class Transaction(Printable):
    """A transaction which can be added to a block in the blockchain.

    Attributes:
        :sender: The sender of the coins.
        :recipient: The recipient of the coins.
        :amount: The amount of coins sent
        :signature: The signatureof the transaction.
    """

    def __init__(self, sender, recipient, amount, signature):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_ordered_dict(self):
        return OrderedDict(
            [
                ("sender", self.sender),
                ("recipient", self.recipient),
                ("amount", self.amount),
                ("signature", self.signature),
            ]
        )
