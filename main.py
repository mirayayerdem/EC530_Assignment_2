from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest
from pydantic import BaseModel

app = FastAPI()

users = {}
houses = {}
floors ={}
rooms = {}
devices = {}
hallways = {}


class User(BaseModel):
    user_id : int
    name : str

class Device(BaseModel):
    device_id : int
    device_type: str
    device_info : int

class Hallway(BaseModel):
    hallway_id : int 
    name : str
    devices : list[Device] = []

class Room(BaseModel):
    room_id : int 
    name : str
    devices : list[Device] = []

class Floor(BaseModel):
    floor_id : int
    name:str
    rooms: list[Room] = []
    hallways: list[Hallway] = []
    devices: list[Device] = []

class House(BaseModel):
    house_id: int
    name:str
    owner: User
    devices: list[Device] = []
    floors: list[Floor] = []
    
#USER
@app.post("/users", response_model=User)
def create_user(user: User):
    if user.user_id in users:
        raise HTTPException(status_code=400, detail="User already exists")
    users[user.user_id] = user
    return user

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    del users[user_id]
    return {"message": "User deleted successfully"}
#HOUSE
@app.post("/house", response_model=House)
def create_house(house :House):
    if house.house_id in houses:
        raise HTTPException(status_code=400, detail="House already exists")
    if house.owner.user_id not in users:
        raise HTTPException(status_code=400, detail="House already exists")

    houses[house.house_id] = house
    return house

@app.get("/house/{house_id}", response_model=House)
def get_house(house_id: int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    return houses[house_id]

##ADD Dependencies
@app.delete("/house/{house_id}")
def delete_house(house_id: int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if  len(houses[house_id].floors) !=0:
        for floor in houses[house_id].floors:
            del floors[floor.floor_id]
    del houses[house_id]
    return {"message": "House deleted successfully"}

#FLOOR
@app.post("/house/{house_id}/floor", response_model=Floor)
def create_floor(house_id:int, floor: Floor):
    if floor.floor_id in floors:
        raise HTTPException(status_code=400, detail="Floor already exists")
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    floors[floor.floor_id] = floor
    houses[house_id].floors.append(floor)
    return floor

@app.get("/house/{house_id}/floors/{floor_id}", response_model=Floor)
def get_floor(floor_id: int):
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floors not found")
    return floors[floor_id]

##ADD Dependencies
@app.delete("/house/{house_id}/floor/{floor_id}")
def delete_floor(house_id:int, floor_id: int):
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if len(floors[floor_id].rooms ) !=0:
        for room in floors[floor_id].rooms:
            del rooms[room.room_id]
    if len(floors[floor_id].hallways) !=0:
        for hallway in floors[floor_id].hallways:
            del hallways[hallway.hallway_id]
    del floors[floor_id]
    return {"message": "Floor deleted successfully"}


@app.post("/house/{house_id}/floor/{floor_id}/room", response_model=Room)
def create_room(house_id:int, floor_id:int, room: Room):
    if room.room_id in rooms:
        raise HTTPException(status_code=400, detail="Room already exists")
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    rooms[room.room_id] = room
    floors[floor_id].rooms.append(room)
    return room

@app.get("/house/{house_id}/floor/{floor_id}/room/{room_id}", response_model=Room)
def get_room(room_id: int):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Rooms not found")
    return rooms[room_id]

##ADD Dependencies
@app.delete("/house/{house_id}/floor/{floor_id}/room/{room_id}")
def delete_room(house_id:int, floor_id: int, room_id:int):
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    del rooms[room_id]
    return {"message": "Room deleted successfully"}

#HALLWAY
@app.post("/house/{house_id}/floor/{floor_id}/hallway", response_model=Hallway)
def create_room(house_id:int, floor_id:int, hallway: Hallway):
    if hallway.hallway_id in hallways:
        raise HTTPException(status_code=400, detail="Hallway already exists")
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    hallways[hallway.hallway_id] = hallway
    floors[floor_id].hallways.append(hallways)
    return hallway

@app.get("/house/{house_id}/floor/{floor_id}/room/{room_id}", response_model=Room)
def get_room(room_id: int):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Rooms not found")
    return rooms[room_id]

##ADD Dependencies
@app.delete("/house/{house_id}/floor/{floor_id}/room/{room_id}")
def delete_room(house_id:int, floor_id: int, room_id:int):
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    del rooms[room_id]
    return {"message": "Room deleted successfully"}



client = TestClient(app)

@pytest.fixture
def setup_users():
    client.post("/users", json={"user_id": 1, "name": "John Doe"})

def test_create_user(setup_users):
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"

def test_create_duplicate_user():
    client.post("/users", json={"user_id": 2, "name": "Alice"})
    response = client.post("/users", json={"user_id": 2, "name": "Alice"})
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"

def test_delete_user():
    client.post("/users", json={"user_id": 3, "name": "Bob"})
    response = client.delete("/users/3")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"
    response = client.get("/users/3")
    assert response.status_code == 404

def test_create_house():
    response = client.post("/house", json={
        "house_id": 1,
        "name": "Dream House",
        "owner": {"user_id": 1, "name": "John Doe"},
        "devices": [],
        "floors": []
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Dream House"

def test_create_duplicate_house():
    response = client.post("/house", json={
        "house_id": 1,
        "name": "Dream House",
        "owner": {"user_id": 1, "name": "John Doe"},
        "devices": [],
        "floors": []
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "House already exists"

def test_delete_house():
    response = client.delete("/house/1")
    assert response.status_code == 200
    assert response.json()["message"] == "House deleted successfully"
    response = client.get("/house/1")
    assert response.status_code == 404

# Test Floor Operations
def test_create_floor():
    client.post("/house", json={"house_id": 2, "name": "Test House", "owner": {"user_id": 1, "name": "John Doe"}, "devices": [], "floors": []})
    response = client.post("/house/2/floor", json={"floor_id": 101, "name": "First Floor", "rooms": [], "hallways": [], "devices": []})
    assert response.status_code == 200
    assert response.json()["name"] == "First Floor"

def test_delete_floor():
    response = client.delete("/house/2/floor/101")
    assert response.status_code == 200
    assert response.json()["message"] == "Floor deleted successfully"
    response = client.get("/house/2/floors/101")
    assert response.status_code == 404

# Test Room Operations
def test_create_room():
    client.post("/house/2/floor", json={"floor_id": 102, "name": "Second Floor", "rooms": [], "hallways": [], "devices": []})
    response = client.post("/house/2/floor/102/room", json={"room_id": 201, "name": "Living Room", "devices": []})
    assert response.status_code == 200
    assert response.json()["name"] == "Living Room"

def test_delete_room():
    response = client.delete("/house/2/floor/102/room/201")
    assert response.status_code == 200
    assert response.json()["message"] == "Room deleted successfully"
    response = client.get("/house/2/floor/102/room/201")
    assert response.status_code == 404

# Test Edge Cases
def test_delete_non_existent_user():
    response = client.delete("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_create_floor_in_non_existent_house():
    response = client.post("/house/999/floor", json={"floor_id": 105, "name": "Ghost Floor", "rooms": [], "hallways": [], "devices": []})
    assert response.status_code == 404
    assert response.json()["detail"] == "House not found"

def test_create_room_in_non_existent_floor():
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






