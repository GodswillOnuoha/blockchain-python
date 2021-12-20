import json
import hashlib as hl


def hash_string_256(string):
    return hl.sha256(string).hexdigest()


def hash_block(block):
    """Hash a block and return a string representation of it.

    Arguments:
        :block: The block that should be hashed
    """
    hashable_block = block.__dict__.copy()
    hashable_block["transactions"] = [
        tx.to_ordered_dict() for tx in hashable_block["transactions"]
    ]
    return hl.sha256(json.dumps(hashable_block, sort_keys=True).encode()).hexdigest()