import os
import sys
from pathlib import Path

os.environ["DB__URL"] = (
    "postgresql+asyncpg://postgres:1290qwer@localhost:5432/test_chat"
)

sys.path.append(str(Path(__file__).resolve().parents[1]))

import uvicorn

from tests.settings import host, port

if __name__ == "__main__":
    uvicorn.run("main:app", host=host, port=int(port), reload=True)
