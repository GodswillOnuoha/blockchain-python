"""Test /nodes endpoint"""


def test_add_node(client):
    """Tests adding a peer node"""
    node = "test-url.com"
    response = client.post("/nodes", json={"node": node})
    data = response.get_json()

    assert response.status_code == 201
    assert data["message"] == "Node successfully added"
    assert node in data["nodes"]


def test_view_nodes(client):
    """Queries peer nodes"""
    response = client.get("/nodes")
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Nodes successfully fetched"
    assert isinstance(data["nodes"], list)


def test_delete_node(client):
    """Deletes a node"""
    response1 = client.get("/nodes")
    # Pick a node
    node = response1.get_json()["nodes"][0]
    assert node != "" and node is not None

    # Delete the node
    response2 = client.delete(f"/nodes/{node}")
    assert response2.status_code == 200

    # Confirm node no longer exists
    response1 = client.get("/nodes")
    nodes = response1.get_json()["nodes"]
    assert node not in nodes
