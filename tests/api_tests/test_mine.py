"""test /mine endpoint"""


def test_mine(client):
    """Mine coin"""
    response = client.post("/mine")
    data = response.get_json()
    transaction = data["block"]["transactions"][0]

    assert response.status_code == 201
    assert data["message"] == "Block added succeffully"

    # Block attributes return
    assert list(data["block"].keys()) == [
        "index",
        "previous_hash",
        "proof",
        "timestamp",
        "transactions",
    ]

    # Transactions
    assert transaction["amount"] == 10
    assert transaction["signature"] == ""
    assert transaction["recipient"] is not None
    assert transaction["sender"] == "MINING"
