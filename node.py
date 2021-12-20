from utility.file import save_data
from utility.verification import Verifier
from blockchain import Blockchain
from uuid import uuid4


class Node:
    def __init__(self):
        self.id = str(uuid4())
        self.blockchain = Blockchain(self.id)

    def get_transaction_value(self):
        tx_recipient = input("Enter the recipient: ")
        tx_amount = float(input("your transaction amount please: "))
        return tx_recipient, tx_amount

    def get_user_choice(self):
        user_input = input("Your choice: ")
        return user_input

    def print_blockchain_elements(self):
        # output the blockchain to console
        for block in self.blockchain.chain:
            print("Outputing block")
            print(block)

    def listen_for_input(self):
        while True:
            print("Please choose")
            print("1: Add a new transaction value")
            print("2: Mine a new block")
            print("3: Print blockchain blocks")
            print("q: Quit")

            user_choice = self.get_user_choice()

            if user_choice == "1":
                recipient, amount = self.get_transaction_value()
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print("Added transaction")
                else:
                    print("Transaction failed")
            elif user_choice == "2":
                self.blockchain.min_block()
            elif user_choice == "3":
                self.print_blockchain_elements()
            elif user_choice == "q":
                break
            else:
                print("Input was invalid, please pick a value from the list!")

            if not Verifier.verify_chain(self.blockchain.chain):
                print("Invalid chain")
                break
            print(f"Balance of {self.id}: {self.blockchain.get_balance():6.2f}")


if __name__ == "__main__":
    node = Node()
    node.listen_for_input()
