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
