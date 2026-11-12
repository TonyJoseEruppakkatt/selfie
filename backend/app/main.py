
import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging_config import configure_logging
from app.database.session import get_db


# Configure logging
configure_logging()

logger = logging.getLogger(__name__)


# Initialize FastAPI
app = FastAPI(
    title="Selfie API",
    description="Used Mobile Buying and Selling Platform",
    version="1.0.0"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Homepage
@app.get("/")
def home():

    logger.info("Selfie API homepage accessed")

    return {
        "message": "Welcome to Selfie API",
        "status": "success"
    }


# Application health check
@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "application": "Selfie"
    }


# Database health check
@app.get("/health/database")
def database_health(db: Session = Depends(get_db)):

    try:

        db.execute(text("SELECT 1"))

        logger.info("MySQL database connection successful")

        return {
            "status": "connected",
            "database": "MySQL"
        }

    except Exception:

        logger.exception("MySQL database connection failed")

        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable"
        )
