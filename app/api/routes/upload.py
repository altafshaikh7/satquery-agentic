import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile


router = APIRouter()


# =========================================================
# UPLOAD CONFIGURATION
# =========================================================

UPLOAD_DIRECTORY = Path("data/uploads")

ALLOWED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


# =========================================================
# HELPER FUNCTION
# =========================================================

def get_file_extension(filename: str) -> str:
    """
    Extract and normalize the uploaded file extension.
    """

    return Path(filename).suffix.lower()


# =========================================================
# UPLOAD SATELLITE IMAGE
# =========================================================

@router.post("/")
async def upload_satellite_image(
    file: UploadFile = File(...),
):
    """
    Upload a satellite image for SatQuery AI analysis.

    Supported formats:
    - PNG
    - JPG
    - JPEG
    - TIFF
    - TIF
    """

    # -----------------------------------------------------
    # VALIDATE FILENAME
    # -----------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    # -----------------------------------------------------
    # VALIDATE FILE EXTENSION
    # -----------------------------------------------------

    extension = get_file_extension(
        file.filename
    )

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file format. "
                "Allowed formats are: "
                "PNG, JPG, JPEG, TIFF, TIF."
            ),
        )

    # -----------------------------------------------------
    # CREATE UPLOAD DIRECTORY
    # -----------------------------------------------------

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------
    # CREATE UNIQUE FILE NAME
    # -----------------------------------------------------

    unique_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = (
        UPLOAD_DIRECTORY
        / unique_filename
    )

    # -----------------------------------------------------
    # READ FILE CONTENT
    # -----------------------------------------------------

    try:
        file_content = await file.read()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to read uploaded file: "
                f"{str(error)}"
            ),
        ) from error

    # -----------------------------------------------------
    # VALIDATE FILE SIZE
    # -----------------------------------------------------

    if len(file_content) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=(
                "File is too large. "
                "Maximum allowed size is 20 MB."
            ),
        )

    # -----------------------------------------------------
    # SAVE FILE
    # -----------------------------------------------------

    try:
        file_path.write_bytes(
            file_content
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save uploaded image: "
                f"{str(error)}"
            ),
        ) from error

    finally:
        await file.close()

    # -----------------------------------------------------
    # SUCCESS RESPONSE
    # -----------------------------------------------------

    return {
        "status": "success",
        "message": (
            "Satellite image uploaded successfully."
        ),
        "filename": file.filename,
        "saved_filename": unique_filename,
        "image_path": str(
            file_path.resolve()
        ),
        "file_size_bytes": len(
            file_content
        ),
    }