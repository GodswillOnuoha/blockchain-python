"""
Old Node packege used when building out the logic
Keeping for reference
"""

# from uuid import uuid4

# from blockchain.utility.file import save_data
# from blockchain.utility.verification import Verifier
# from blockchain.blockchain import Blockchain
# from blockchain.wallet import Wallet


# class Node:
#     def __init__(self):
#         self.wallet = Wallet()
#         self.wallet.creat_keys()
#         self.blockchain = Blockchain(self.wallet.public_key)

#     def get_transaction_value(self):
#         tx_recipient = input("Enter the recipient: ")
#         tx_amount = float(input("your transaction amount please: "))
#         return tx_recipient, tx_amount

#     def get_user_choice(self):
#         user_input = input("Your choice: ")
#         return user_input

#     def print_blockchain_elements(self):
#         # output the blockchain to console
#         for block in self.blockchain.chain:
#             print("Outputing block")
#             print(block)

#     def start(self):
#         while True:
#             print("Please choose")
#             print("1: Add a new transaction value")
#             print("2: Mine a new block")
#             print("3: Print blockchain blocks")
#             print("4: Create wallet")
#             print("5: Save wallet")
#             print("6: Load wallet")
#             print("q: Quit")

#             user_choice = self.get_user_choice()

#             if user_choice == "1":
#                 recipient, amount = self.get_transaction_value()
#                 signature = self.wallet.sign_transaction(
#                     self.wallet.public_key, recipient, amount
#                 )
#                 if self.blockchain.add_transaction(
#                     recipient, self.wallet.public_key, signature, amount=amount
#                 ):
#                     print("Added transaction")
#                 else:
#                     print("Transaction failed")
#             elif user_choice == "2":
#                 if not self.blockchain.mine_block():
#                     print("Mining failed. Need a wallet")
#             elif user_choice == "3":
#                 self.print_blockchain_elements()
#             elif user_choice == "4":
#                 self.wallet.creat_keys()
#                 self.blockchain = Blockchain(self.wallet.public_key)
#             elif user_choice == "5":
#                 self.wallet.save_keys()
#             elif user_choice == "6":
#                 self.wallet.load_keys()
#                 self.blockchain = Blockchain(self.wallet.public_key)
#             elif user_choice == "q":
#                 break
#             else:
#                 print("Input was invalid, please pick a value from the list!")

#             if not Verifier.verify_chain(self.blockchain.chain):
#                 print("Invalid chain")
#                 break
#             print(
#                 f"Balance of {self.wallet.public_key}: {self.blockchain.get_balance():6.2f}"
#             )


# if __name__ == "__main__":
#     node = Node()
#     node.listen_for_input()
