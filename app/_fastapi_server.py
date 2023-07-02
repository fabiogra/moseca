from fastapi import FastAPI
from fastapi.responses import FileResponse
from urllib.parse import unquote

import os

app = FastAPI()


@app.get("/streaming/{path:path}")
async def serve_streaming(path: str):
    # Decode URL-encoded characters
    decoded_path = unquote(path)
    return FileResponse(decoded_path, filename=os.path.basename(decoded_path))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
