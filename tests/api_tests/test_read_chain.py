"""Test /chain."""


def test_read_blockchain(client):
    """Test that endpoint returns a list of blocks"""
    response = client.get("/chain")
    block = response.get_json()[0]

    assert response.status_code == 200
    assert list(block.keys()) == [
        "index",
        "previous_hash",
        "proof",
        "timestamp",
        "transactions",
    ]
