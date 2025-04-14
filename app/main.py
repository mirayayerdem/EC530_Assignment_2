from fastapi import FastAPI, HTTPException, Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import  Literal
from db_tables import Base, User as DBUser, House as DBHouse, Floor as DBFloor, Room as DBRoom, Hallway as DBHallway, Device as DBDevice
from database import engine, SessionLocal
Base.metadata.create_all(bind=engine)

app = FastAPI()
# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
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

class UserOut(User):
    user_id: int
    class Config:
        orm_mode = True

class Device(BaseModel):
    device_id: int
    device_type: Literal["humidity", "temperature"]  # Only allow 'humidity' or 'temperature'
    device_info : int

class DeviceOut(Device):
    device_id: int
    class Config:
        orm_mode = True

class Hallway(BaseModel):
    hallway_id : int 
    name : str
    devices : list[Device] = []

class HallwayOut(Hallway):
    hallway_id: int
    class Config:
        orm_mode = True

class Room(BaseModel):
    room_id : int 
    name : str
    devices : list[Device] = []

class RoomOut(Room):
    room_id: int
    class Config:
        orm_mode = True

class Floor(BaseModel):
    floor_id : int
    name:str
    rooms: list[Room] = []
    hallways: list[Hallway] = []

class FloorOut(Floor):
    floor_id: int
    class Config:
        orm_mode = True

class House(BaseModel):
    house_id: int
    name:str
    owner: User
    floors: list[Floor] = []
class HouseOut(House):
    house_id: int
    class Config:
        orm_mode = True

class UpdatedObject(BaseModel):
    name: str
class UpdatedDevice(BaseModel):
    device_info: int
    
#USER
@app.post("/users", response_model=UserOut)
def create_user(user: User, db: Session = Depends(get_db)):
    db_user = DBUser(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UpdatedObject, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

#HOUSE
@app.post("/house", response_model=HouseOut)
def create_house(house: House, db: Session = Depends(get_db)):
    owner = db.query(DBUser).filter(DBUser.user_id == house.owner_id).first()
    if not owner:
        raise HTTPException(status_code=400, detail="Owner does not exist")
    db_house = DBHouse(name=house.name, owner_id=house.owner_id)
    db.add(db_house)
    db.commit()
    db.refresh(db_house)
    return db_house


@app.patch("/house/{house_id}", response_model=HouseOut)
def update_house(house_id: int, house: UpdatedObject, db: Session = Depends(get_db)):
    db_house = db.query(DBHouse).filter(DBHouse.house_id == house_id).first()
    if not db_house:
        raise HTTPException(status_code=404, detail="House not found")
    db_house.name = house.name
    db.commit()
    db.refresh(db_house)
    return db_house


@app.get("/house/{house_id}", response_model=HouseOut)
def get_house(house_id: int, db: Session = Depends(get_db)):
    db_house = db.query(DBHouse).filter(DBHouse.house_id == house_id).first()
    if not db_house:
        raise HTTPException(status_code=404, detail="House not found")
    return db_house

##ADD Dependencies
@app.delete("/house/{house_id}")
def delete_house(house_id: int, db: Session = Depends(get_db)):
    db_house = db.query(DBHouse).filter(DBHouse.house_id == house_id).first()
    if not db_house:
        raise HTTPException(status_code=404, detail="House not found")
    db.delete(db_house)
    db.commit()
    return {"message": "House deleted successfully"}

#FLOOR
@app.post("/house/{house_id}/floor", response_model=FloorOut)
def create_floor(house_id: int, floor: Floor, db: Session = Depends(get_db)):
    house = db.query(DBHouse).filter(DBHouse.house_id == house_id).first()
    if not house:
        raise HTTPException(status_code=404, detail="House not found")
    db_floor = DBFloor(name=floor.name, house_id=house_id)
    db.add(db_floor)
    db.commit()
    db.refresh(db_floor)
    return db_floor

@app.patch("/house/{house_id}/floor/{floor_id}", response_model=FloorOut)
def update_floor(house_id: int, floor_id: int, floor: UpdatedObject, db: Session = Depends(get_db)):
    db_floor = db.query(DBFloor).filter(DBFloor.floor_id == floor_id, DBFloor.house_id == house_id).first()
    if not db_floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    db_floor.name = floor.name
    db.commit()
    db.refresh(db_floor)
    return db_floor
                

@app.get("/house/{house_id}/floor/{floor_id}", response_model=FloorOut)
def get_floor(house_id: int, floor_id: int, db: Session = Depends(get_db)):
    db_floor = db.query(DBFloor).filter(DBFloor.floor_id == floor_id, DBFloor.house_id == house_id).first()
    if not db_floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    return db_floor


@app.delete("/house/{house_id}/floor/{floor_id}")
def delete_floor(house_id: int, floor_id: int, db: Session = Depends(get_db)):
    db_floor = db.query(DBFloor).filter(DBFloor.floor_id == floor_id, DBFloor.house_id == house_id).first()
    if not db_floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    db.delete(db_floor)
    db.commit()
    return {"message": "Floor deleted successfully"}

#ROOM
@app.post("/house/{house_id}/floor/{floor_id}/room", response_model=RoomOut)
def create_room(house_id: int, floor_id: int, room: Room, db: Session = Depends(get_db)):
    floor = db.query(DBFloor).filter(DBFloor.floor_id == floor_id, DBFloor.house_id == house_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    db_room = DBRoom(name=room.name, floor_id=floor_id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@app.patch("/house/{house_id}/floor/{floor_id}/room/{room_id}", response_model=RoomOut)
def update_room(house_id: int, floor_id: int, room_id: int, room: UpdatedObject, db: Session = Depends(get_db)):
    db_room = db.query(DBRoom).filter(DBRoom.room_id == room_id, DBRoom.floor_id == floor_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    db_room.name = room.name
    db.commit()
    db.refresh(db_room)
    return db_room


@app.get("/house/{house_id}/floor/{floor_id}/room/{room_id}", response_model=RoomOut)
def get_room(house_id: int, floor_id: int, room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(DBRoom).filter(DBRoom.room_id == room_id, DBRoom.floor_id == floor_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room


##ADD Dependencies
@app.delete("/house/{house_id}/floor/{floor_id}/room/{room_id}")
def delete_room(house_id: int, floor_id: int, room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(DBRoom).filter(DBRoom.room_id == room_id, DBRoom.floor_id == floor_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    db.delete(db_room)
    db.commit()
    return {"message": "Room deleted successfully"}

#HALLWAY
@app.post("/house/{house_id}/floor/{floor_id}/hallway", response_model=HallwayOut)
def create_hallway(house_id: int, floor_id: int, hallway: Hallway, db: Session = Depends(get_db)):
    floor = db.query(DBFloor).filter(DBFloor.floor_id == floor_id, DBFloor.house_id == house_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    db_hallway = DBHallway(name=hallway.name, floor_id=floor_id)
    db.add(db_hallway)
    db.commit()
    db.refresh(db_hallway)
    return db_hallway

@app.patch("/house/{house_id}/floor/{floor_id}/hallway/{hallway_id}", response_model=HallwayOut)
def update_hallway(house_id: int, floor_id: int, hallway_id: int, hallway: UpdatedObject, db: Session = Depends(get_db)):
    db_hallway = db.query(DBHallway).filter(DBHallway.id == hallway_id, DBHallway.floor_id == floor_id).first()
    if not db_hallway:
        raise HTTPException(status_code=404, detail="Hallway not found")
    db_hallway.name = hallway.name
    db.commit()
    db.refresh(db_hallway)
    return db_hallway

@app.get("/house/{house_id}/floor/{floor_id}/hallway/{hallway_id}", response_model=HallwayOut)
def get_hallway(house_id: int, floor_id: int, hallway_id: int, db: Session = Depends(get_db)):
    db_hallway = db.query(DBHallway).filter(DBHallway.hallway_id == hallway_id, DBHallway.floor_id == floor_id).first()
    if not db_hallway:
        raise HTTPException(status_code=404, detail="Hallway not found")
    return db_hallway


@app.delete("/house/{house_id}/floor/{floor_id}/hallway/{hallway_id}")
def delete_hallway(house_id: int, floor_id: int, hallway_id: int, db: Session = Depends(get_db)):
    db_hallway = db.query(DBHallway).filter(DBHallway.hallway_id == hallway_id, DBHallway.floor_id == floor_id).first()
    if not db_hallway:
        raise HTTPException(status_code=404, detail="Hallway not found")
    db.delete(db_hallway)
    db.commit()
    return {"message": "Hallway deleted successfully"}

#DEVICE

@app.post("/house/{house_id}/floor/{floor_id}/hallway/{hallway_id}/device", response_model=DeviceOut)
def create_device_hallway(house_id: int, floor_id: int, hallway_id: int, device: Device, db: Session = Depends(get_db)):
    hallway = db.query(DBHallway).filter(DBHallway.hallway_id == hallway_id, DBHallway.floor_id == floor_id).first()
    if not hallway:
        raise HTTPException(status_code=404, detail="Hallway not found")
    db_device = DBDevice(device_type=device.device_type, device_info=device.device_info, hallway_id=hallway_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@app.post("/house/{house_id}/floor/{floor_id}/room/{room_id}/device", response_model=DeviceOut)
def create_device_to_room(house_id:int, floor_id:int, room_id: int,device: Device, db: Session = Depends(get_db)):
    room = db.query(DBRoom).filter(DBRoom.room_id == room_id, DBRoom.floor_id == floor_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    db_device = DBDevice(device_type=device.device_type, device_info=device.device_info, device_id=device_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@app.get("/device/{device_id}", response_model=DeviceOut)
def get_device(device_id: int, db: Session = Depends(get_db)):
    db_device = db.query(DBDevice).filter(DBDevice.device_id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device

@app.patch("/device/{device_id}", response_model=DeviceOut)
def update_device(device_id: int, device: UpdatedDevice, db: Session = Depends(get_db)):
    db_device = db.query(DBDevice).filter(DBDevice.device_id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    db_device.device_info = device.device_info
    db.commit()
    db.refresh(db_device)
    return db_device 

@app.delete("/device/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    db_device = db.query(DBDevice).filter(DBDevice.device_id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(db_device)
    db.commit()
    return {"message": "Device deleted successfully"}
