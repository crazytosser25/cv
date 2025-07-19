import os
import redis.asyncio as redis
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter.depends import RateLimiter
from fastapi_limiter import FastAPILimiter


# Global constants
r = None
origins = [
    "*",
]

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Define the lifespan of the FastAPI application.

    This function manages the lifecycle of the FastAPI application, initializing and closing
    resources such as Redis and FastAPILimiter during the app's lifespan.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        Allows the FastAPI application to run within this context, managing resources.
    """
    global r
    r = await redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        db=0, encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)

    yield

    r.close()


# Routers
#  Rotes to load pages
pages_router = APIRouter(tags=["Pages"])

@pages_router.get("/", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
async def main_page():
    return FileResponse("static/index.html")

#  Rotes to load docs
docs_router = APIRouter(tags=["Downloads"])

@docs_router.get("/download/cv", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
async def load_cv():
    return FileResponse("static/docs/CV_YBaranov.pdf")

@docs_router.get("/download/lebenslauf", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
async def load_lebenslauf():
    return FileResponse("static/docs/Lebenslauf_YBaranov.pdf")

# Routes for service purposes
service_router = APIRouter(tags=["Service"])

@service_router.get("/healthchecker", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
def root() -> dict:
    """Health check endpoint to verify that the server is running.

    This endpoint can be used to confirm that the server is alive and
    responding to requests. It returns a simple message indicating the server
    status.

    Returns:
        dict: A dictionary containing a message indicating that
            the server is alive.
    """
    result = {"message": "Server alive."}
    return result

@service_router.get("/favicon.ico", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
async def favicon():
    return FileResponse("static/images/favicon.ico")

@service_router.get("/css/styles.css", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
async def css():
    return FileResponse("static/css/styles.css")

@service_router.get("/images/photo", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
async def photo():
    return FileResponse("static/images/photo_jask.jpg")


# Start app
app = FastAPI(title="CVs", lifespan=lifespan)

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
app.include_router(pages_router)
app.include_router(docs_router)
app.include_router(service_router)
