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
- **Push notification**
  - Real-time push notification via websocket
- **Admin**
  - Admin endpoints
- **Image**
  - User can upload avatar
- **Clean project structure**
  - Separation of routes, services, and schemas
  - Separation of api and websocket server
  - Custom and flexible exception handling
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
- [RabbitMQ](https://www.rabbitmq.com/) - for message queue
- [Redis](https://redis.io/) - for synchronize websockets of multiple server instanses 
- [Nginx](https://nginx.org/) - for reverse proxy
---

## API Preview
<img width="960" height="479" alt="auth" src="https://github.com/user-attachments/assets/63e755bf-172a-4180-bfa0-0b66f4b77cff" />
<img width="960" height="483" alt="chat" src="https://github.com/user-attachments/assets/3dc414b8-8f41-448a-a242-5aa7d26eff2c" />
<img width="960" height="480" alt="websocket" src="https://github.com/user-attachments/assets/9752a546-9053-4f0c-9801-9437256b7676" />

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

# 7. Up docket-compose
docker-compose up
```

---

## Documentation

API doc: http://localhost/docs#

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
