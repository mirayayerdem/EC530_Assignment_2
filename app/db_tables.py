from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class DeviceTypeEnum(enum.Enum):
    humidity = "humidity"
    temperature = "temperature"

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    houses = relationship("House", back_populates="owner")

class House(Base):
    __tablename__ = "houses"
    house_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.user_id"))
    
    owner = relationship("User", back_populates="houses")
    floors = relationship("Floor", back_populates="house", cascade="all, delete")

class Floor(Base):
    __tablename__ = "floors"
    floor_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    house_id = Column(Integer, ForeignKey("houses.house_id"))
    
    house = relationship("House", back_populates="floors")
    rooms = relationship("Room", back_populates="floor", cascade="all, delete")
    hallways = relationship("Hallway", back_populates="floor", cascade="all, delete")

class Room(Base):
    __tablename__ = "rooms"
    room_id = Column(Integer, primary_key=True)
    name = Column(String)
    floor_id = Column(Integer, ForeignKey("floors.floor_id"))
    
    floor = relationship("Floor", back_populates="rooms")
    devices = relationship("Device", back_populates="room", cascade="all, delete")

class Hallway(Base):
    __tablename__ = "hallways"
    hallway_id = Column(Integer, primary_key=True)
    name = Column(String)
    floor_id = Column(Integer, ForeignKey("floors.floor_id"))
    
    floor = relationship("Floor", back_populates="hallways")
    devices = relationship("Device", back_populates="hallway", cascade="all, delete")

class Device(Base):
    __tablename__ = "devices"
    device_id = Column(Integer, primary_key=True)
    device_type = Column(Enum(DeviceTypeEnum))
    device_info = Column(Integer)

    room_id = Column(Integer, ForeignKey("rooms.room_id"), nullable=True)
    hallway_id = Column(Integer, ForeignKey("hallways.hallway_id"), nullable=True)

    room = relationship("Room", back_populates="devices")
    hallway = relationship("Hallway", back_populates="devices")