
import logging
from io import BytesIO
import cloudinary
import cloudinary.uploader

from fastapi import HTTPException, status

from app.core.config import settings


logger = logging.getLogger(__name__)


def configure_cloudinary() -> None:
    """
    Configure Cloudinary using environment variables.
    """

    if not all([
        settings.CLOUDINARY_CLOUD_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET
    ]):
        logger.error("Cloudinary credentials are missing")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image storage is not configured"
        )

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )



def upload_mobile_image(image_content: bytes) -> dict:
    try:
        configure_cloudinary()

        image_file = BytesIO(image_content)

        result = cloudinary.uploader.upload(
            image_file,
            folder="selfie/mobile_images",
            resource_type="image",
        )

        image_data = {
            "image_url": result["secure_url"],
            "public_id": result["public_id"],
        }

        logger.info(
            "Mobile image uploaded successfully: %s",
            image_data["public_id"],
        )

        return image_data

    except HTTPException:
        raise

    except Exception:
        logger.exception("Cloudinary image upload failed")

        raise HTTPException(
            status_code=502,
            detail="Unable to upload mobile image",
        )

def delete_mobile_image(public_id: str) -> bool:
    """
    Delete a mobile image from Cloudinary.

    Returns:
        True if deletion succeeds or image is already missing.
        False if deletion fails.
    """

    try:

        configure_cloudinary()

        result = cloudinary.uploader.destroy(
            public_id,
            resource_type="image"
        )

        deletion_status = result.get("result")

        if deletion_status in ["ok", "not found"]:

            logger.info(
                "Cloudinary image deleted: %s",
                public_id
            )

            return True

        logger.warning(
            "Cloudinary image deletion unsuccessful: %s",
            public_id
        )

        return False

    except Exception:

        logger.exception(
            "Cloudinary image deletion failed: %s",
            public_id
        )

        return False
