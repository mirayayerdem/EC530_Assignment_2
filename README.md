# EC530_Assignment_2
# Miray Ayerdem
# API Guide for House Environment System

##  House Environment System Overview

This  application provides a structured way to manage users, houses, floors, rooms, hallways, and devices in a smart home system. The API allows CRUD (Create, Read, Update, Delete) operations on these entities with built-in error handling and validation.

## Base URL

```
http://localhost:8000
```

## API Endpoints

### 1. Users

#### Create a User

**POST /users**

```json
{
  "user_id": 1,
  "name": "Miray Ayerdem"
}
```

*Response:*

```json
{
  "user_id": 1,
  "name": "Miray Ayerdem"
}
```

#### Get a User

**GET /users/{user\_id}** *Response:*

```json
{
  "user_id": 1,
  "name": "Miray Ayerdem"
}
```

#### Update a User

**PATCH /users/{user\_id}**

```json
{
  "name": "Joe Doe"
}
```

*Response:*

```json
{
  "user_id": 1,
  "name": "Joe Doe"
}
```

#### Delete a User

**DELETE /users/{user\_id}** *Response:*

```json
{
  "message": "User deleted successfully"
}
```

---

### 2. Houses

#### Create a House

**POST /house**

```json
{
  "house_id": 1,
  "name": "Smart House",
  "owner": {
    "user_id": 1,
    "name": "John Doe"
  },
  "floors": []
}
```

*Response:*

```json
{
  "house_id": 1,
  "name": "Smart House",
  "owner": {
    "user_id": 1,
    "name": "John Doe"
  },
  "floors": []
}
```

#### Get a House

**GET /house/{house\_id}** *Response:*

```json
{
  "house_id": 1,
  "name": "Smart House",
  "owner": {
    "user_id": 1,
    "name": "John Doe"
  },
  "floors": []
}
```

#### Update a House

**PATCH /house/{house\_id}**

```json
{
  "name": "Luxury House"
}
```

*Response:*

```json
{
  "house_id": 1,
  "name": "Luxury House",
  "owner": {
    "user_id": 1,
    "name": "John Doe"
  },
  "floors": []
}
```

#### Delete a House

**DELETE /house/{house\_id}** *Response:*

```json
{
  "message": "House deleted successfully"
}
```

---

### 3. Floors

#### Create a Floor

**POST /house/{house\_id}/floor**

```json
{
  "floor_id": 1,
  "name": "Basement Floor",
  "rooms": [],
  "hallways": []
}
```

*Response:*

```json
{
  "floor_id": 1,
  "name": "Basement Floor",
  "rooms": [],
  "hallways": []
}
```

#### Delete a Floor

**DELETE /house/{house\_id}/floor/{floor\_id}** *Response:*

```json
{
  "message": "Floor deleted successfully"
}
```

---

### 4. Rooms

#### Create a Room

**POST /house/{house\_id}/floor/{floor\_id}/room**

```json
{
  "room_id": 1,
  "name": "Living Room",
  "devices": []
}
```

*Response:*

```json
{
  "room_id": 1,
  "name": "Living Room",
  "devices": []
}
```

#### Delete a Room

**DELETE /house/{house\_id}/floor/{floor\_id}/room/{room\_id}** *Response:*

```json
{
  "message": "Room deleted successfully"
}
```

---

### 5. Devices

#### Add a Device to a Room

There are two types of devices: temperature and humidity and these devices can be added only hallways and rooms.

**POST /house/{house\_id}/floor/{floor\_id}/room/{room\_id}/device**

```json
{
  "device_id": 1,
  "device_type": "temperature",
  "device_info": 20
}
```

*Response:*

```json
{
  "device_id": 1,
  "device_type": "temperature",
  "device_info": 20
}
```

#### Delete a Device

**DELETE /house/{house\_id}/floor/{floor\_id}/room/{room\_id}/device/{device\_id}** *Response:*

```json
{
  "message": "Device deleted successfully"
}
```

## Error Handling

All endpoints return appropriate HTTP error responses when required. Examples:

- `404 Not Found` if the requested resource does not exist.
- `400 Bad Request` if invalid data is provided.

## Running the API

To start the API server, use the following command:

```bash
uvicorn app.main:app --reload
```

This will serve the API on `http://localhost:8000`.

## Running Tests

To run unit tests, execute:

```bash
pytest
```

Additionally, one can enter the host given after executing

```bash
uvicorn app.main:app --reload
```   
and use the apis in the docs section of the host. e.g. http://127.0.0.1:8000/docs.
