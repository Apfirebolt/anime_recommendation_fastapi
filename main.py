from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
# import uvicorn
from contextlib import asynccontextmanager
import logging

from routes.anime import router as anime_router

# Configure logger for the anime app
logger = logging.getLogger("anime_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for managing application startup and shutdown events.
    """
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")

app = FastAPI(
    title="Anime Recommendation API",
    description="A FastAPI backend for exploring anime datasets and fetching precomputed similarity recommendations.",
    docs_url="/docs",
    lifespan=lifespan,
    version="0.1.0"
)

# CORS configuration for Next.js frontend
origins = [
    "http://localhost:8080", 
    "http://localhost:3000",
    "https://animerecommendationfrontend.vercel.app",
    "https://animelounge.in",
    "https://www.animelounge.in"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register pagination and routers
add_pagination(app)
app.include_router(anime_router)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the FastAPI Anime Recommendation System!"}

@app.get("/api/health")
async def health_check():
    return {"message": "FastAPI Anime Recommendation API is healthy"}

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)