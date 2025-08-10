from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from settings import print_settings, settings
from database import engine
from admin.router import router as admin_router
from media.router import router as media_router
from users.router import router as users_router
from auth.router import router as auth_router
from chat.router import router as chat_router


@asynccontextmanager
async def lifestyle(app: FastAPI):
    print_settings()
    settings.media.upload_path.mkdir(exist_ok=True)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifestyle)

from core import exception_handlers

app.include_router(admin_router)
app.include_router(media_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(chat_router)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
def read_root():
    return HTMLResponse(content=html, media_type="text/html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000, log_level="info", reload=True)
