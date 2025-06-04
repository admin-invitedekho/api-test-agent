# InviteDeKho API Contracts

## Base Configuration

**Base URL**: `https://api.stage.invitedekho.com`  
**Content-Type**: `application/json`

## Authentication

### Login Endpoint

**Method**: `POST`  
**Endpoint**: `/login`  
**Description**: Authenticates users and returns JWT token

#### Request Schema

```json
{
  "type": "object",
  "required": ["email", "password"],
  "properties": {
    "email": {
      "type": "string",
      "format": "email"
    },
    "password": {
      "type": "string"
    }
  }
}
```

#### Success Response (200 OK)

```json
{
  "jwtToken": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI5NDEyODE3NjY3IiwiaWF0IjoxNzQ4NTQ1Njc0LCJleHAiOjE3NDkxNTA0NzR9.LHcp5OGhF1mKjdlss8ErdHzHKsBhc87Bt-KoiXlzbXY"
}
```

## User Profile

### Get User Profile Endpoint

**Method**: `GET`  
**Endpoint**: `/user/me`  
**Description**: Retrieves the authenticated user's profile information  
**Authentication**: Required (Bearer Token)

#### cURL Command

```bash
curl --location 'http://api.stage.invitedekho.com/user/me' \
--header 'Accept: */*' \
--header 'Authorization: Bearer {{bearerToken}}'
```

#### Request Headers

- `Accept: */*`
- `Authorization: Bearer {jwtToken}` (Required)

#### Success Response (200 OK)

```json
{
  "id": 1,
  "email": "admin@invitedekho.com",
  "firstName": "Vibhor",
  "lastName": "Goyal",
  "phone": "9412817667",
  "createdDate": "2024-08-20T10:22:52.971149",
  "userRole": "ADMIN",
  "extraData": {
    "location": "400001",
    "howDidYouHearOthers": "",
    "howDidYouHear": "Facebook"
  },
  "enabled": true
}
```

#### Response Schema

```json
{
  "type": "object",
  "required": ["id", "email", "firstName", "lastName", "phone"],
  "properties": {
    "id": {
      "type": "integer"
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "firstName": {
      "type": "string"
    },
    "lastName": {
      "type": "string"
    },
    "phone": {
      "type": "string"
    },
    "createdDate": {
      "type": "string",
      "format": "date-time"
    },
    "userRole": {
      "type": "string",
      "enum": ["ADMIN", "USER"]
    },
    "extraData": {
      "type": "object"
    },
    "enabled": {
      "type": "boolean"
    }
  }
}
```

#### Error Responses

- **401 Unauthorized**: Invalid or missing Bearer token
- **403 Forbidden**: Token valid but user not authorized
- **404 Not Found**: User not found
