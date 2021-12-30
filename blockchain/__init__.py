"""Entry point"""

from blockchain.node import Node


def create_node():
    """Exposes a blockchain node. Call start on node to start it"""
    node = Node()
    return node
