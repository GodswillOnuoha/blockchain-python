import requests

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
        genesis_block = Block(0, "", [], 100, timestamp=1640090462.789401)
        # Initializing empty blockchain
        self.chain = [genesis_block]
        # Unhandled transactions
        self.__open_transactions = []
        self.hosting_node = hosting_node_id
        self.__peer_nodes = set()
        self.resolve_conflicts = False

        try:
            self.chain, self.__open_transactions, self.__peer_nodes = load_data()
        except (FileNotFoundError, IndexError):
            pass

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def save_data(self):
        """Saves Blockchain, open transactions and peer nodes to file"""
        save_data(self.__chain, self.__open_transactions, self.__peer_nodes)

    def add_node(self, node):
        """Adds a node to the chain

        Arguments:
            :node: The node URL to be added
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_node(self, node):
        """Removes a node from the chain

        Arguments:
            :node: The node URL to remove
        """
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_nodes(self):
        """Returns a list of connected peer nodes"""
        return list(self.__peer_nodes)

    def get_open_transactions(self):
        """Returns a copy of open transactions"""
        return self.__open_transactions[:]

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verifier.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self, sender=None):
        if sender == None:
            if self.hosting_node == None:
                return None

            participant = self.hosting_node
        else:
            participant = sender
        # Fetch all sent transaction for the user
        # fetches amount of transactions already included in blockchain
        tx_sender = [
            [tx.amount for tx in block.transactions if tx.sender == participant]
            for block in self.__chain
        ]
        # Fetches amount of all transactions yet to be mined. to avoid double spending
        open_tx_sender = [
            tx.amount for tx in self.__open_transactions if tx.sender == participant
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
                recieved_amount += sum(tx)
        return recieved_amount - sent_amount

    def get_last_blockchain_value(self):
        """Returns the last value of the current blockchain."""
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(
        self, recipient, sender, signature, amount=1.0, is_broadcast=False
    ):
        if self.hosting_node == None:
            return False

        transaction = Transaction(sender, recipient, amount, signature)
        if Verifier.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()

            if not is_broadcast:
                # Broadcast transaction
                for node in self.__peer_nodes:
                    url = f"http://{node}/broadcast-transaction"
                    try:
                        response = requests.post(
                            url,
                            json={
                                "sender": sender,
                                "recipient": recipient,
                                "amount": amount,
                                "signature": signature,
                            },
                        )
                        if not response.status_code == 200:
                            print("Transaction declined")
                            return False
                    except requests.exceptions.ConnectionError:
                        continue

            return True
        return False

    def mine_block(self):
        if self.hosting_node == None:
            return None

        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction("MINING", self.hosting_node, MINING_REWARD, "")

        # Copy transaction and not modify the original
        # This ensures that if mining fails, we do not add reward transaction
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None

        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)

        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()

        converted_block = block.__dict__.copy()
        converted_block["transactions"] = [
            tx.__dict__ for tx in converted_block["transactions"]
        ]
        for node in self.__peer_nodes:
            url = f"http://{node}/broadcast-block"
            try:
                response = requests.post(url, json={"block": converted_block})
                if response.status_code == 500 or response.status_code == 400:
                    print("Block declined")
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def resolve_conflict(self):
        """Resolves conflict when in chain"""
        winning_chain = self.__chain
        replaced = False
        for node in self.__peer_nodes:
            url = f"http://{node}/chain"

            try:
                response = requests.get(url)
                node_chain = response.json()
                # Pick the valid and longest chain
                if len(node_chain) > len(winning_chain):
                    node_chain = [
                        Block(
                            block["index"],
                            block["previous_hash"],
                            [
                                Transaction(
                                    tx["sender"],
                                    tx["recipient"],
                                    tx["amount"],
                                    tx["signature"],
                                )
                                for tx in block["transactions"]
                            ],
                            block["proof"],
                            block["timestamp"],
                        )
                        for block in node_chain
                    ]
                    if Verifier.verify_chain(node_chain):
                        winning_chain = node_chain
                        replaced = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflicts = False
        self.__chain = winning_chain
        if replaced:
            self.__open_transactions = []
        self.save_data()
        return replaced

    def add_block(self, block):
        transactions = [
            Transaction(tx["sender"], tx["recipient"], tx["amount"], tx["signature"])
            for tx in block["transactions"]
        ]
        # Remove Mining reward transaction as it wasn't used in proof calculation
        proof_is_valid = Verifier.valid_proof(
            transactions[:-1], block["previous_hash"], block["proof"]
        )
        hash_match = hash_block(self.__chain[-1]) == block["previous_hash"]

        if not proof_is_valid or not hash_match:
            return False
        blk = Block(
            block["index"],
            block["previous_hash"],
            transactions,
            block["proof"],
            block["timestamp"],
        )
        self.__chain.append(blk)

        # Update open transactions to remove transactions in newly mined block
        open_transactions = self.__open_transactions[:]
        for mtx in block["transactions"]:
            for open_tx in open_transactions:
                if (open_tx.sender, open_tx.recipient, open_tx.signature) == (
                    mtx["sender"],
                    mtx["recipient"],
                    mtx["signature"],
                ):
                    try:
                        self.__open_transactions.remove(open_tx)
                    except ValueError:
                        print("Open tx already removed")
        self.save_data()
        return True
