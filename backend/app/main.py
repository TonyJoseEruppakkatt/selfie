
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Selfie API",
    description="Used Mobile Buying and Selling Platform",
    version="1.0.0"
)

# Configure frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    logger.info("Selfie API homepage accessed")

    return {
        "message": "Welcome to Selfie API",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Selfie"
    }
