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

# Global memory storage for ML model and precomputed vectors
ml_cache = {
    "model": None,
    "records": None,
    "vectors": None
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for managing application startup and shutdown events.
    Loads the SentenceTransformer model and precomputed anime cache into RAM.
    """
    logger.info("Application starting up: Loading AI model and precomputed pickle cache...")
    
    try:
        # Load the model
        ml_cache["model"] = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load the precomputed cache file
        with open("anime_cache.pkl", "rb") as f:
            cache_data = pickle.load(f)
            ml_cache["records"] = cache_data["records"]
            ml_cache["vectors"] = cache_data["vectors"]
            
        logger.info("Successfully loaded %d anime records and vectors into memory!", len(ml_cache["records"]))
    except Exception as e:
        logger.error("Failed to load ML model or anime_cache.pkl during startup: %s", str(e), exc_info=True)

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