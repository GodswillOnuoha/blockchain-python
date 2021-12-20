from blockchain.node import Node

def create_node():
    """Exposes a blockchain node. Call listen_for_input on node to start a node"""
    node = Node()
    return node