from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest
from pydantic import BaseModel, Field
from typing import Optional, Literal
import logging
app = FastAPI()

users = {}
houses = {}
floors ={}
rooms = {}
devices = {}
hallways = {}
user_id =0
house_id=0
floor_id=0
room_id=0
device_id=0
hallway_id = 0

def delete_floor_by_id(floor_id: int):
    # Remove rooms in the floor
    for room in floors[floor_id].rooms:
        if room.room_id in rooms:
            del rooms[room.room_id]
    # Remove hallways in the floor
    for hallway in floors[floor_id].hallways:
        if hallway.hallway_id in hallways:
            del hallways[hallway.hallway_id]
    # Finally, delete the floor
    del floors[floor_id]

def delete_room_by_id(room_id: int):
    for dev in rooms[room_id].devices:
        if dev.device_id in devices:
            del devices[dev.device_id]  
    del rooms[room_id]

def delete_hallway_by_id(hallway_id: int):
    for dev in hallways[hallway_id].devices:
        if dev.device_id in devices:
            del devices[dev.device_id]  
    del hallways[hallway_id]


def get_new_id(id):
    id = id +1
    return id

class User(BaseModel):
    user_id : int
    name : str = Field(..., min_length=3, max_length=50)

class Device(BaseModel):
    device_id: int
    device_type: Literal["humidity", "temperature"]  # Only allow 'humidity' or 'temperature'
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

class House(BaseModel):
    house_id: int
    name:str
    owner: User
    floors: list[Floor] = []

class UpdatedObject(BaseModel):
    name: str
class UpdatedDevice(BaseModel):
    device_info: int
    
#USER
@app.post("/users", response_model=User)
def create_user(user:User):
    if user.user_id in users:
        raise HTTPException(status_code=400, detail="User already exists")
    users[user.user_id] = user
    return user

@app.patch("/users/{user_id}")
def update_user(user_id: int, user: UpdatedObject):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    if user.name:
        old_user = users[user_id]
        updated_user = old_user.model_copy(update={"name": user.name})
        users[user_id] = updated_user  # Only update the name field
        for house in houses:
            if users[user_id] in house.owner:
                house.owner = updated_user
                users[user_id] = updated_user
    return users[user_id]


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
        raise HTTPException(status_code=400, detail="Owner doesnt exist")

    # Check if the owner's name matches the one stored in `users`
    if house.owner.name != users[house.owner.user_id].name:
        raise HTTPException(status_code=400, detail="Owner name mismatch")
    houses[house.house_id] = house
    return house

@app.patch("/house/{house_id}")
def update_house(house_id: int, house: UpdatedObject):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    
    if house.name:
        old_house = houses[house_id]
        updated_house = old_house.model_copy(update={"name": house.name})
        houses[house_id] = updated_house
    return houses[house_id]


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
    for i, f in enumerate(houses[house_id].floors):
        if f.floor_id == floor_id:
            delete_floor_by_id(floor_id)
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

@app.patch("/house/{house_id}/floors/{floor_id}")
def update_floor(house_id:int, floor_id: int, floor: UpdatedObject):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    for i, f in enumerate(houses[house_id].floors):
        if f.floor_id == floor_id:
            if floor.name:
                old_floor = floors[floor_id]
                updated_floor = old_floor.model_copy(update={"name": floor.name})
                floors[floor_id] = updated_floor
                houses[house_id].floors[i] = updated_floor
                return floors[floor_id]
    raise HTTPException(status_code=404, detail="This floor doesnt exist in thr house")
                

@app.get("/house/{house_id}/floors/{floor_id}", response_model=Floor)
def get_floor(floor_id: int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    for i, f in enumerate(houses[house_id].floors):
        if f.floor_id == floor_id:
            return floors[floor_id]
    raise HTTPException(status_code=404, detail="This floor doesnt exist in the house")

@app.delete("/house/{house_id}/floor/{floor_id}")
def delete_floor(house_id:int, floor_id: int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")

    for i, f in enumerate(houses[house_id].floors):
        if f.floor_id == floor_id:
            del houses[house_id].floors[i]
            delete_floor_by_id(floor_id)
            return {"message": "Floor deleted successfully"}
    raise HTTPException(status_code=404, detail="This floor doesnt exist in the house")

#ROOM
@app.post("/house/{house_id}/floor/{floor_id}/room", response_model=Room)
def create_room(house_id:int, floor_id:int, room: Room):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if room.room_id in rooms:
        raise HTTPException(status_code=400, detail="Room already exists")

    rooms[room.room_id] = room
    floors[floor_id].rooms.append(room)
    return room

@app.patch("/house/{house_id}/floors/{floor_id}/room/{room_id}")
def update_room(house_id:int, floor_id: int, room_id:int,  room: UpdatedObject):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Rooms not found")
    for i, r in enumerate(floors[floor_id].rooms):
        if r.room_id == room_id:
            if room.name:
                    old_room =  rooms[room_id]
                    updated_room = old_room.model_copy(update={"name": room.name})
                    rooms[room_id] = updated_room
                    floors[floor_id].rooms[i] = updated_room
                    return rooms[room_id]
    raise HTTPException(status_code=404, detail="This room doesnt exist in the specified floor")


@app.get("/house/{house_id}/floor/{floor_id}/room/{room_id}", response_model=Room)
def get_room(room_id: int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Rooms not found")
    for i, r in enumerate(floors[floor_id].rooms):
        if r.room_id == room_id:
            return rooms[room_id]
    raise HTTPException(status_code=404, detail="This room doesnt exist in the specified floor")


##ADD Dependencies
@app.delete("/house/{house_id}/floor/{floor_id}/room/{room_id}")
def delete_room(house_id:int, floor_id: int, room_id:int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Rooms not found")
    for i, r in enumerate(floors[floor_id].rooms):
        if r.room_id == room_id:
            delete_room_by_id(room_id)
            del floors[floor_id].rooms[i]
            return {"message": "Room deleted successfully"}
    raise HTTPException(status_code=404, detail="This room doesnt exist in the specified floor")

#HALLWAY
@app.post("/house/{house_id}/floor/{floor_id}/hallway", response_model=Hallway)
def create_hallway(house_id:int, floor_id:int, hallway: Hallway):
    if hallway.hallway_id in hallways:
        raise HTTPException(status_code=400, detail="Hallway already exists")
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    hallways[hallway.hallway_id] = hallway
    floors[floor_id].hallways.append(hallway)
    return hallway

@app.patch("/house/{house_id}/floors/{floor_id}/hallway/{hallway_id}")
def update_hallway(house_id:int, floor_id: int, hallway_id:int,  hallway: UpdatedObject):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if hallway_id not in hallways:
        raise HTTPException(status_code=404, detail="Hallway not found")
    for i, h in enumerate(floors[floor_id].hallways):
        if h.hallway_id == hallway_id:
            if hallway.name:
                old_hallway = hallways[hallway_id]
                updated_hallway = old_hallway.model_copy(update={"name": hallway.name})
                hallways[hallway_id] = updated_hallway
                floors[floor_id].hallways[i] = updated_hallway
            return hallways[hallway_id]
    raise HTTPException(status_code=404, detail="This hallway doesnt exist in the specified floor")

@app.get("/house/{house_id}/floor/{floor_id}/hallway/{hallway_id}", response_model=Hallway)
def get_hallway(hallway_id: int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if hallway_id not in hallways:
        raise HTTPException(status_code=404, detail="Hallway not found")
    for i, h in enumerate(floors[floor_id].hallways):
        if h.hallway_id == hallway_id:
            return hallways[hallway_id]
    raise HTTPException(status_code=404, detail="This hallway doesnt exist in the specified floor")


@app.delete("/house/{house_id}/floor/{floor_id}/hallway/{hallway_id}")
def delete_hallway(house_id:int, floor_id: int, hallway_id:int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if hallway_id not in hallways:
        raise HTTPException(status_code=404, detail="Hallway not found")
   
    for i, h in enumerate(floors[floor_id].hallways):
        if h.hallway_id == hallway_id:
            del floors[floor_id].hallways[i]
            delete_hallway_by_id(hallway_id)
            return {"message": "Hallway deleted successfully"}
    raise HTTPException(status_code=404, detail="This hallway doesnt exist in the specified floor")

#DEVICE

@app.post("/house/{house_id}/floor/{floor_id}/hallway/{hallway_id}/device", response_model=Device)
def create_device_to_hallway(house_id:int, floor_id:int, hallway_id: int, device:Device):
    if hallway_id not in hallways:
        raise HTTPException(status_code=404, detail="Hallway not found")
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    devices[device.device_id] = device
    hallways[hallway_id].devices.append(device)
    return device

@app.post("/house/{house_id}/floor/{floor_id}/room/{room_id}/device", response_model=Device)
def create_device_to_room(house_id:int, floor_id:int, room_id: int, device:Device):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    devices[device.device_id] = device
    rooms[room_id].devices.append(device)
    return device

@app.patch("/house/{house_id}/floor/{floor_id}/hallway/{hallway_id}/device/{device_id}")
def update_device_hallway(house_id:int, floor_id: int, hallway_id:int, device_id:int,  device: UpdatedDevice):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if hallway_id not in hallways:
        raise HTTPException(status_code=404, detail="Hallway not found")
    
    for i, d in enumerate(hallways[hallway_id].devices):
            if d.device_id == device_id:
                if device.device_info:
                    old_device = devices[device_id]
                    updated_device = old_device.model_copy(update={"device_info": device.device_info})
                    devices[device_id] = updated_device
                    hallways[hallway_id].devices[i] = updated_device
                    return devices[device_id]
    raise HTTPException(status_code=404, detail="Device not found in hallway")

@app.patch("/house/{house_id}/floor/{floor_id}/room/{room_id}/device/{device_id}")
def update_device_room(house_id:int, floor_id: int, room_id:int, device_id:int,  device: UpdatedDevice):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    for i, d in enumerate(rooms[room_id].devices):
            if d.device_id == device_id:
                if device.device_info is not None:
                    old_device = devices[device_id]
                    updated_device = old_device.model_copy(update={"device_info": device.device_info})
                    devices[device_id] = updated_device
                    rooms[room_id].devices[i] = updated_device
                    return updated_device
    raise HTTPException(status_code=404, detail="Device not found in room")
  

@app.get("/house/{house_id}/floor/{floor_id}/hallway/{hallway_id}/device/{device_id}", response_model=Device)
def get_hallway_device(house_id:int, floor_id:int, hallway_id: int, device_id:int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if hallway_id not in hallways:
        raise HTTPException(status_code=404, detail="Hallway not found")
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    for i, d in enumerate(hallways[hallway_id].devices):
            if d.device_id == device_id:
                 return devices[device_id]
    raise HTTPException(status_code=404, detail="Device not found in the hallway")

@app.get("/house/{house_id}/floor/{floor_id}/room/{room_id}/device/{device_id}", response_model=Device)
def get_room_device(house_id:int, floor_id:int, room_id: int, device_id:int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    for i, d in enumerate(rooms[room_id].devices):
            if d.device_id == device_id:
                 return devices[device_id]
    raise HTTPException(status_code=404, detail="Device not found in the room")

@app.delete("/house/{house_id}/floor/{floor_id}/hallway/{hallway_id}/device/{device_id}")
def delete_hallway_device(house_id:int, floor_id: int, hallway_id:int, device_id:int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if hallway_id not in hallways:
        raise HTTPException(status_code=404, detail="Hallway not found")
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    for i, d in enumerate(hallways[hallway_id].devices):
            if d.device_id == device_id:
                del hallways[hallway_id].devices[i]
                del devices[device_id]
                return {"message": "Device deleted successfully"}

    raise HTTPException(status_code=404, detail="Device not found in the hallway")

@app.delete("/house/{house_id}/floor/{floor_id}/room/{room_id}/device/{device_id}")
def delete_room_device(house_id:int, floor_id: int, room_id:int, device_id:int):
    if house_id not in houses:
        raise HTTPException(status_code=404, detail="House not found")
    if floor_id not in floors:
        raise HTTPException(status_code=404, detail="Floor not found")
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    for i, d in enumerate(rooms[room_id].devices):
            if d.device_id == device_id:
                del rooms[room_id].devices[i]
                del devices[device_id]
                return {"message": "Device deleted successfully"}

    raise HTTPException(status_code=404, detail="Device not found in the room")


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







