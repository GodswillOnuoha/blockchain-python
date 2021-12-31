"""Initialise test params"""

import os
import pytest

from blockchain.node import app
from blockchain.utility.file import FILE_NAME as chain_file
from blockchain.wallet import FILE_NAME as wallet_file


def reset_data():
    """Delete blockchain and wallet text files."""
    try:
        os.remove(chain_file)
        os.remove(wallet_file)
    except FileNotFoundError:
        pass


@pytest.fixture
def client():
    """App test client"""
    _client = app.test_client()
    # Create wallet keys
    _client.post("/wallet")
    # mine block
    _client.post("/mine")
    yield _client
    reset_data()
