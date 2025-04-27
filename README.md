# Lead Management API

A FastAPI application for managing leads, including submission, retrieval, and status updates.

## System Design

The application follows a layered architecture:

1. **API Layer**: FastAPI endpoints for lead submission, retrieval, and updates
2. **Authentication Layer**: JWT-based authentication for protected endpoints
3. **Service Layer**: Business logic for lead management and email notifications
4. **Data Layer**: SQLite database for persistent storage

### Components:

- **FastAPI Application**: Handles HTTP requests and responses
- **SQLAlchemy ORM**: Manages database operations
- **Pydantic Models**: Validates request and response data
- **JWT Authentication**: Secures internal endpoints
- **Email Service**: Sends notifications to prospects and attorneys

## Features

- Public lead submission form with file upload
- Email notifications to prospects and attorneys
- Authenticated access to lead management
- Lead status tracking (PENDING, REACHED_OUT)
- API documentation with OpenAPI

## API Endpoints

### Public Endpoints

- `POST /leads/`: Submit a new lead with first name, last name, email, and resume
- `POST /token`: Authenticate and get access token

### Protected Endpoints (require authentication)

- `GET /leads/`: Get all leads with optional filtering by state
- `GET /leads/{lead_id}`: Get a specific lead by ID
- `PUT /leads/{lead_id}`: Update a lead's state

## Setup and Installation

1. Clone the repository
2. Install dependencies:
    ```bash
   pipenv shell
    pipenv install
   ```
    or if you are not using pipenv:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   uvicorn main:app --reload
   ```

## Usage Examples

### Submit a Lead (Public)

```bash
curl -X POST http://localhost:8000/leads/ \
  -F "first_name=John" \
  -F "last_name=Doe" \
  -F "email=john.doe@example.com" \
  -F "resume=@/path/to/resume.pdf"
```

### Authenticate

```bash
curl -X POST http://localhost:8000/token \
  -d "username=attorney&password=password" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

### Get All Leads (Authenticated)

```bash
curl -X GET http://localhost:8000/leads/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Update Lead Status (Authenticated)

```bash
curl -X PUT http://localhost:8000/leads/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"state": "REACHED_OUT"}'
```

## Documentation

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Security Considerations

- In production, use a secure random key for JWT token generation
- Store sensitive configuration in environment variables
- Implement proper email server configuration
- Add rate limiting to prevent abuse
- Consider adding CORS protection

## Demo Link
It is hosted on: http://alma.shahr.am/
