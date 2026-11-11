
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.material import Material
from app.models.subject import Subject
from app.schemas.material import MaterialResponse


router = APIRouter(tags=["Materials"])


ALLOWED_FILES = {
    ".pdf": {
        "mime": "application/pdf",
        "signature": b"%PDF-",
    },
    ".pptx": {
        "mime": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "signature": b"PK",
    },
    ".docx": {
        "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "signature": b"PK",
    },
}

CHUNK_SIZE = 1024 * 1024


@router.post(
    "/subjects/{subject_id}/materials",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_material(
    subject_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 1. Verify that the subject exists.
    subject = db.query(Subject).filter(
        Subject.id == subject_id
    ).first()

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="Subject not found",
        )

    # 2. Validate the file extension.
    original_filename = (
        file.filename or "uploaded_file"
    ).replace("\\", "/").split("/")[-1]

    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_FILES:
        raise HTTPException(
            status_code=415,
            detail="Only PDF, PPTX and DOCX files are supported",
        )

    file_info = ALLOWED_FILES[extension]

    # 3. Validate the reported MIME type.
    if file.content_type not in (
        file_info["mime"],
        "application/octet-stream",
        None,
    ):
        raise HTTPException(
            status_code=415,
            detail="File content type does not match its extension",
        )

    # 4. Prepare a unique storage location.
    material_id = uuid4()

    storage_directory = (
        settings.STORAGE_DIR / str(subject_id)
    )

    storage_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    storage_filename = f"{material_id}{extension}"
    destination = storage_directory / storage_filename

    total_size = 0
    first_chunk = True

    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    try:
        # 5. Stream the upload to disk in chunks.
        with destination.open("wb") as output:

            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > max_size:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 25 MB upload limit",
                    )

                # 6. Check the file's basic signature.
                if first_chunk:
                    first_chunk = False

                    if not chunk.startswith(file_info["signature"]):
                        raise HTTPException(
                            status_code=415,
                            detail="File signature is invalid",
                        )

                output.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty",
            )

        # 7. Save metadata in PostgreSQL.
        material = Material(
            id=material_id,
            subject_id=subject_id,
            original_filename=original_filename[:255],
            storage_path=str(
                Path(str(subject_id)) / storage_filename
            ),
            mime_type=file_info["mime"],
            file_size_bytes=total_size,
            status="uploaded",
        )

        db.add(material)
        db.commit()
        db.refresh(material)

        return material

    except HTTPException:
        db.rollback()
        destination.unlink(missing_ok=True)
        raise

    except Exception:
        db.rollback()
        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Unable to save uploaded material",
        )

    finally:
        await file.close()


@router.get(
    "/subjects/{subject_id}/materials",
    response_model=list[MaterialResponse],
)
def get_subject_materials(
    subject_id: UUID,
    db: Session = Depends(get_db),
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id
    ).first()

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="Subject not found",
        )

    materials = (
        db.query(Material)
        .filter(Material.subject_id == subject_id)
        .order_by(Material.uploaded_at.desc())
        .all()
    )

    return materials
