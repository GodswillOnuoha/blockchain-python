from blockchain.utility.hash_util import hash_block, hash_string_256
from blockchain.wallet import Wallet


class Verifier:
    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        guess = (
            str([tx.to_ordered_dict() for tx in transactions])
            + str(last_hash)
            + str(proof)
        ).encode()
        guess_hash = hash_string_256(guess)
        return guess_hash[:3] == "000"

    @classmethod
    def verify_chain(cls, blockchain):
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(
                block.transactions[:-1], block.previous_hash, block.proof
            ):
                print("Prof of work is invalid")
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_fund=True):
        """Verify transaction by checking signature, and that the sender has sufficient balance

        Arguments:
            :transaction: The transaction that should be verified
            :get_balance: The function that retuns user's balance
            :check_fund: Flag to check balance. function checks only signature if check_fund is false
        """
        if check_fund:
            sender_balance = get_balance()
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        return Wallet.verify_transaction(transaction)

    # def verify_transactions(self, transactions, get_balance):
    #     """Verify transactions by checking that the sender has sufficient balance for each transaction

    #     Arguments:
    #         :trannsactions: The transactions that should be verified
    #     """
    #     return all([self.verify_transaction(tx, get_balance, False) for tx in transactions])
