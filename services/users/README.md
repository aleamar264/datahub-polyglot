# Users Service

A microservice for managing user accounts and authentication as part of the DataHub-Polyglot platform.

## Features

- User management (CRUD operations)
- Role-based access control
- Email verification
- Password management
- Kafka event publishing for user activities
- RESTful API with HATEOAS links
- Authentication endpoints (register, login, email verification, password reset)

## Tech Stack

- Python 3.11+
- FastAPI
- FastStream (Kafka integration)
- SQLAlchemy (async)
- Pydantic v2
- PostgreSQL
- Redis (for caching and token management)

## API Endpoints

### User Management
| Method | Endpoint              | Description                    |
|--------|----------------------|--------------------------------|
| GET    | /users              | List all users                 |
| GET    | /users/{uuid}       | Get specific user              |
| PUT    | /users/{uuid}       | Update user                    |
| DELETE | /users/{uuid}       | Delete user                    |
| POST   | /users/soft_delete  | Soft delete user               |

### Authentication
| Method | Endpoint                      | Description                          |
|--------|-------------------------------|--------------------------------------|
| POST   | /auth/register                | Register a new user                  |
| POST   | /auth/login                   | Log in to an account                 |
| GET    | /auth/verify-email            | Verify email address                 |
| POST   | /auth/resend-verification     | Resend email verification link       |
| POST   | /auth/request-password-reset  | Request password reset               |
| POST   | /auth/reset-password          | Reset password                       |

## Quick Start

1. Clone the repository:
```bash
git clone git@github.com:your-org/DataHub-Polyglot.git
cd services/users
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the service:
```bash
uvicorn src.main:app --reload
```

## Event Publishing

The service publishes the following Kafka events:
- `user.created`
- `user.updated`
- `user.deleted`
- `user.verification_token.created`
- `user.password_reset.requested`

## Project Structure

```
services/users/
├── src/
│   ├── models/      # Database models
│   ├── repository/  # Database operations
│   ├── routes/      # API endpoints
│   ├── schema/      # Pydantic models
│   └── utils/       # Helper functions
├── tests/           # Unit tests
└── README.md
```

## Development

- Run tests: `pytest`
- Format code: `black .`
- Check types: `mypy .`
- Lint code: `ruff .`

## Documentation

API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

[MIT License](LICENSE)