# Chat Application with JWT Authentication and WebSocket

This is a simple backend project built with **FastAPI** that demonstrates:
- **User authentication** using JWT
- **Real-time chat** functionality with WebSockets

Perfect as a learning project or a starting point for more complex applications.

---

## Features

- **JWT-based authentication**
  - Sign up / Sign in endpoints
  - Secure password hashing
  - Token validation middleware
- **Real-time chat**
  - WebSocket-based communication
  - Private chat rooms by `chat_id`
  - Broadcast messages to all connected users in the room
- **Admin**
  - Admin endpoints
- **Image**
  - User can upload avatar
- **Clean project structure**
  - Separation of routes, services, and schemas
  - Easy to extend

---

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) — web framework
- [PyJWT](https://pyjwt.readthedocs.io/) — JWT implementation
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM
- [PostgreSQL](https://www.postgresql.org/) — database (can be replaced)
- [Alembic](https://alembic.sqlalchemy.org/) - database migration tool
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
- [Pytest](https://docs.pytest.org/en/stable/) - testing tool
---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/aibert-enni/chat
cd project-name

# 2. Install Poetry (if not already installed)
pip install poetry

# 3. Install dependencies
poetry install

# 4. Init tables with alembic
poetry alembic upgrade head

# 5. Init private and public key for jwt
mkdir certs

cd certs

openssl genrsa -out jwt-private.pem 2048
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem 

cd ..

# 6. Set environment variables
cp .env.example .env
# Edit .env file with your database URL, JWT secret, etc.

# 7. Get to src directory
cd src

# 8. Run the application
poetry run uvicorn app.main:app --reload
```

---

## Documentation

API doc: http://localhost:8000/docs#

[Websocket documentation](docs/WEBSOCKET_API.md)

You can also test WebSocket via test_websocket.html in the project.

---
## Test
```bash
# 1. create test database and set db url in run_test_server.py

# 2. run test server
cd src
poetry run py run_test_server.py

# 3. run pytest and check tests
poetry run pytest
```