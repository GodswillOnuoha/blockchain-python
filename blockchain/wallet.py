from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import binascii

FILE_NAME = "wallet.txt"


class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def creat_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def save_keys(self):
        if not self.private_key == None and not self.public_key == None:
            try:
                with open(FILE_NAME, "w") as f:
                    f.write(self.private_key)
                    f.write("\n")
                    f.write(self.public_key)
            except (FileNotFoundError, IndexError):
                print("Saving wallet failed ...")

    def load_keys(self):
        try:
            with open(FILE_NAME, "r") as f:
                keys = f.readlines()
                self.private_key = keys[0][:-1]
                self.public_key = keys[1]
        except (FileNotFoundError, IndexError):
            print("Loading wallet failed ...")

    def generate_keys(self):
        private_key = RSA.generate(2048)
        public_key = private_key.publickey()
        return (
            binascii.hexlify(private_key.export_key(format="DER")).decode("ascii"),
            binascii.hexlify(public_key.export_key(format="DER")).decode("ascii"),
        )

    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.import_key(binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(recipient) + str(amount)).encode("utf8"))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode("ascii")
    
    @staticmethod
    def verify_transaction(transaction):
        public_key = RSA.import_key(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode("utf8"))
        verified = verifier.verify(h, binascii.unhexlify(transaction.signature))
        return verified
