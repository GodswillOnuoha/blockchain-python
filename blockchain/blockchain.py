from collections import OrderedDict

from blockchain.block import Block
from blockchain.wallet import Wallet
from blockchain.transaction import Transaction
from blockchain.utility.hash_util import hash_block, hash_string_256
from blockchain.utility.file import load_data, save_data
from blockchain.utility.verification import Verifier

MINING_REWARD = 10


class Blockchain:
    def __init__(self, hosting_node_id):
        # Our starting block for the the blockchain
        genesis_block = Block(0, "", [], 100)
        # Initializing empty blockchain
        self.chain = [genesis_block]
        # Unhandled transactions
        self.open_transactions = []
        self.hosting_node = hosting_node_id

        try:
            self.chain, self.open_transactions = load_data()
        except (FileNotFoundError, IndexError):
            pass

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verifier.valid_proof(self.open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        participant = self.hosting_node
        tx_sender = [
            [tx.amount for tx in block.transactions if tx.sender == participant]
            for block in self.__chain
        ]
        open_tx_sender = [
            tx.amount for tx in self.open_transactions if tx.sender == participant
        ]
        tx_sender.append(open_tx_sender)
        sent_amount = 0
        for tx in tx_sender:
            if len(tx) > 0:
                sent_amount += sum(tx)

        tx_recipient = [
            [tx.amount for tx in block.transactions if tx.recipient == participant]
            for block in self.__chain
        ]
        recieved_amount = 0
        for tx in tx_recipient:
            if len(tx) > 0:
                recieved_amount += tx[0]
        return recieved_amount - sent_amount

    def get_last_blockchain_value(self):
        """Returns the last value of the current blockchain."""
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender, signature, amount=1.0):
        if self.hosting_node == None:
            return False

        transaction = Transaction(sender, recipient, amount, signature)
        if Verifier.verify_transaction(transaction, self.get_balance):
            self.open_transactions.append(transaction)
            save_data(self.__chain, self.open_transactions)
            return True
        return False

    def min_block(self):
        if self.hosting_node == None:
            return False

        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction("MINING", self.hosting_node, MINING_REWARD, "")

        # Copy transaction and not modify the original
        # This ensures that if mining fails, we do not add reward transaction
        copied_transactions = self.open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return False

        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)

        self.__chain.append(block)
        self.open_transactions = []
        save_data(self.__chain, self.open_transactions)
        return True
