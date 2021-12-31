"""Test /balance endpoint."""


def test_balance(client):
    """test that endpoint returns balance"""

    response = client.get("/balance")
    data = response.get_json()

    assert response.status_code == 200
    assert data["funds"] == 10
    assert data["message"] == "Fetched balance successfully"
