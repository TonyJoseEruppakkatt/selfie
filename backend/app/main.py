
import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging_config import configure_logging
from app.database.session import get_db
from app.routers.auth import router as auth_router
from app.routers.mobiles import router as mobile_router
from fastapi.openapi.utils import get_openapi
from app.routers.purchase_requests import router as purchase_request_router



# Configure logging
configure_logging()

logger = logging.getLogger(__name__)


# Initialize application
app = FastAPI(
    title="Selfie API",
    description="Used Mobile Buying and Selling Platform",
    version="1.0.0"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register authentication router
app.include_router(auth_router)


@app.get("/")
def home():

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


@app.get("/health/database")
def database_health(
    db: Session = Depends(get_db)
):

    try:

        db.execute(text("SELECT 1"))

        logger.info("MySQL connection successful")

        return {
            "status": "connected",
            "database": "MySQL"
        }

    except Exception:

        logger.exception("MySQL connection failed")

        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable"
        )
app.include_router(mobile_router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    def fix_upload_schema(schema):
        if isinstance(schema, dict):
            if (
                schema.get("type") == "string"
                and schema.get("contentMediaType") == "application/octet-stream"
            ):
                schema.pop("contentMediaType", None)
                schema["format"] = "binary"

            for value in schema.values():
                fix_upload_schema(value)

        elif isinstance(schema, list):
            for item in schema:
                fix_upload_schema(item)

    fix_upload_schema(openapi_schema)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.include_router(purchase_request_router)