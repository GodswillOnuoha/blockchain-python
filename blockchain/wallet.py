"""Exposes a Wallet class"""

import binascii
import os

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

from dotenv import load_dotenv

load_dotenv()

f_env = os.environ.get("FLASK_ENV")
FILE_NAME = f"{f_env}_wallet.txt"


def generate_keys():
    """Generates a new set of keys using RSA"""
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    return (
        binascii.hexlify(private_key.export_key(format="DER")).decode("ascii"),
        binascii.hexlify(public_key.export_key(format="DER")).decode("ascii"),
    )


class Wallet:
    """A wallet to manage keys.

    Attributes:
        private_key: private key.
        public_key: public key.

    Methods:
        create_keys(): Creates keys
        save_keys(): Exports keys to file
        load_keys(): Loads keys from file
        sign_transaction(self, sender, recipient, amount): Returns a signature for the transaction
        verify_transaction(transaction): Verifies that a given transaction was properly signed
    """

    def __init__(self):
        self.private_key = None
        self.public_key = None

    def creat_keys(self):
        """Creates new keys"""
        private_key, public_key = generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def save_keys(self):
        """Saves current keys to a file"""
        if not self.private_key is None and not self.public_key is None:
            try:
                with open(FILE_NAME, "w", encoding="utf-8") as file:
                    file.write(self.private_key)
                    file.write("\n")
                    file.write(self.public_key)
                return True
            except (FileNotFoundError, IndexError):
                print("Saving wallet failed ...")
                return False
        return False

    def load_keys(self):
        """Loads saved keys"""
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as file:
                keys = file.readlines()
                self.private_key = keys[0][:-1]
                self.public_key = keys[1]
            return True
        except (FileNotFoundError, IndexError):
            print("Loading wallet failed ...")
            return False

    def sign_transaction(self, sender, recipient, amount):
        """ "Signs a transaction, Returns signature"""
        signer = PKCS1_v1_5.new(RSA.import_key(binascii.unhexlify(self.private_key)))
        _hash = SHA256.new((str(sender) + str(recipient) + str(amount)).encode("utf8"))
        signature = signer.sign(_hash)
        return binascii.hexlify(signature).decode("ascii")

    @staticmethod
    def verify_transaction(transaction):
        """ "Verifies a signed transaction. Returns true if unchanged"""
        public_key = RSA.import_key(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        _hash = SHA256.new(
            (
                str(transaction.sender)
                + str(transaction.recipient)
                + str(transaction.amount)
            ).encode("utf8")
        )
        verified = verifier.verify(_hash, binascii.unhexlify(transaction.signature))
        return verified
