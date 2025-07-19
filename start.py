"""Starter for FastAPI project with uvicorn"""
import os
from dotenv import load_dotenv
import uvicorn


load_dotenv()
app_host = os.getenv("APP_HOST")
app_port = int(os.getenv("APP_PORT"))


if __name__ == "__main__":
    uvicorn.run(
        app="src.main:app",
        host=app_host,
        port=app_port
    )
