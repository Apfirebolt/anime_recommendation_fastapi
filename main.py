# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
import uvicorn
from contextlib import asynccontextmanager
import logging
import pickle
from sentence_transformers import SentenceTransformer

from routes.anime import router as anime_router
from routes.manga import router as manga_router

# Configure logger for the anime app
logger = logging.getLogger("anime_app")

# Global memory storage for ML model and precomputed vectors for both anime and manga
ml_cache = {
    "model": None,
    "anime": {"records": None, "vectors": None},
    "manga": {"records": None, "vectors": None}
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for managing application startup and shutdown events.
    Loads the SentenceTransformer model and precomputed anime and manga caches into RAM.
    """
    logger.info("Application starting up: Loading AI model and precomputed pickle caches...")
    
    try:
        # Load the shared sentence transformer model
        ml_cache["model"] = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 1. Load Anime Cache
        try:
            with open("anime_cache.pkl", "rb") as f:
                anime_data = pickle.load(f)
                ml_cache["anime"]["records"] = anime_data["records"]
                ml_cache["anime"]["vectors"] = anime_data["vectors"]
            logger.info("Successfully loaded %d anime records into memory!", len(ml_cache["anime"]["records"]))
        except Exception as e:
            logger.warning("Could not load anime_cache.pkl: %s", str(e))

        # 2. Load Manga Cache
        try:
            with open("manga_cache.pkl", "rb") as f:
                manga_data = pickle.load(f)
                ml_cache["manga"]["records"] = manga_data["records"]
                ml_cache["manga"]["vectors"] = manga_data["vectors"]
            logger.info("Successfully loaded %d manga records into memory!", len(ml_cache["manga"]["records"]))
        except Exception as e:
            logger.warning("Could not load manga_cache.pkl: %s", str(e))

    except Exception as e:
        logger.error("Failed to load AI model during startup: %s", str(e), exc_info=True)

    yield
    
    # Shutdown: Clear memory
    logger.info("Application shutting down: Clearing ML cache from RAM...")
    ml_cache.clear()

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
app.include_router(manga_router)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the FastAPI Anime Recommendation System!"}

@app.get("/api/health")
async def health_check():
    return {"message": "FastAPI Anime Recommendation API is healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)