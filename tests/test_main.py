from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest
app = FastAPI()
client = TestClient(app)

@pytest.fixture
def setup_users():
    client.post("/users", json={"user_id": 1, "name": "John Doe"})

def test_create_user(setup_users):
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"

def test_update_user():
    client.post("/users", json={"user_id": 2, "name": "Alice"})
    response = client.patch("/users/2", json={"name": "Updated Alice"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Alice"

def test_delete_user():
    client.post("/users", json={"user_id": 3, "name": "Bob"})
    response = client.delete("/users/3")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"
    response = client.get("/users/3")
    assert response.status_code == 404

# Test House Operations
def test_create_device():
    client.post("/house", json={"house_id": 1, "name": "Test House", "owner": {"user_id": 1, "name": "John Doe"}, "devices": [], "floors": []})
    client.post("/house/1/floor", json={"floor_id": 1, "name": "First Floor", "rooms": [], "hallways": [], "devices": []})
    client.post("/house/1/floor/1/room", json={"room_id": 1, "name": "Living Room", "devices": []})

    response = client.post("/house/1/floor/1/room/1/device", json={
        "device_id": 101,
        "device_type": "temperature",
        "device_info": 22
    })
    assert response.status_code == 200
    assert response.json()["device_type"] == "temperature"

def test_update_house():
    response = client.patch("/house/1", json={"name": "Luxury House"})
    assert response.status_code == 200
    assert response.json()["name"] == "Luxury House"

def test_delete_house():
    client.post("/house", json={"house_id": 2, "name": "Test House", "owner": {"user_id": 1, "name": "John Doe"}, "devices": [], "floors": []})
    response = client.delete("/house/2") 
    assert response.status_code == 200
    assert response.json()["message"] == "House deleted successfully"
    response = client.get("/house/2")
    assert response.status_code == 404

# Test Device Operations
def test_create_device():
    client.post("/house", json={
        "house_id": 1, 
        "name": "Test House", 
        "owner": {"user_id": 1, "name": "John Doe"},
        "devices": [], 
        "floors": []
    })
    client.post("/house/1/floor", json={
        "floor_id": 1, 
        "name": "First Floor", 
        "rooms": [], 
        "hallways": [], 
        "devices": []
    })
    client.post("/house/1/floor/1/room", json={
        "room_id": 1, 
        "name": "Living Room", 
        "devices": []
    })
    response = client.post("/house/1/floor/1/room/1/device", json={
        "device_id": 101,
        "device_type": "temperature",
        "device_info": 22
    })
    assert response.status_code == 200  # Ensure success
    assert response.json()["device_type"] == "temperature"

def test_update_device_room():
    # Step 1: Create User
    client.post("/users", json={"user_id": 0, "name": "John Doe"})

    # Step 2: Create House
    client.post("/house", json={
        "house_id": 0, 
        "name": "Test House", 
        "owner": {"user_id": 0, "name": "John Doe"},
        "floors": []
    })

    # Step 3: Create Floor
    client.post("/house/0/floor", json={
        "floor_id": 0, 
        "name": "First Floor", 
        "rooms": [],
        "hallways": []
    })

    # Step 4: Create Room
    client.post("/house/0/floor/0/hallway", json={
        "hallway_id": 0, 
        "name": "Living Room", 
        "devices": []
    })

    # Step 5: Create Device in the Room
    client.post("/house/0/floor/0/hallway/0/device", json={
        "device_id": 0,
        "device_type": "temperature",
        "device_info": 22
    })

    # Step 6: Update the Device
    response = client.patch("/house/0/floor/0/hallway/0/device/0", json={"device_info": 25})

    # Step 7: Validate Response
    assert response.status_code == 200

    assert response.json()["device_info"] == 25  # Ensure update was applied correctly

def test_delete_non_existent_user():
    response = client.delete("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_create_floor_in_non_existent_house():
    response = client.post("/house/999/floor", json={"floor_id": 105, "name": "A Floor", "rooms": [], "hallways": [], "devices": []})
    assert response.status_code == 404
    assert response.json()["detail"] == "House not found"

def test_create_room_in_non_existent_floor():
    client.post("/house", json={"house_id": 2, "name": "Test House", "owner": {"user_id": 1, "name": "John Doe"}, "devices": [], "floors": []})
    
    response = client.post("/house/2/floor/999/room", json={"room_id": 202, "name": "Non-existent Room", "devices": []})
    assert response.status_code == 404
    assert response.json()["detail"] == "Floor not found"

def test_delete_house_with_floors():
    client.post("/house", json={"house_id": 3, "name": "Test House", "owner": {"user_id": 1, "name": "John Doe"}, "devices": [], "floors": []})
    client.post("/house/3/floor", json={"floor_id": 110, "name": "First Floor", "rooms": [], "hallways": [], "devices": []})
    response = client.delete("/house/3")
    assert response.status_code == 200
    assert response.json()["message"] == "House deleted successfully"
    response = client.get("/house/3")
    assert response.status_code == 404
