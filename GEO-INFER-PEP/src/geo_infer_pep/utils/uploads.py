"""Shared upload helpers for GEO-INFER-PEP API endpoints."""

from pathlib import Path
import tempfile

from fastapi import HTTPException, UploadFile


async def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    """Persist an uploaded file to a temporary path.

    The caller is responsible for unlinking the returned path (typically in a
    ``finally`` block). Raises ``HTTPException(500)`` if the file cannot be
    written.
    """
    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=upload_file.filename
        ) as tmp:
            contents = await upload_file.read()
            tmp.write(contents)
            tmp_path = Path(tmp.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save uploaded file: {e}")
    finally:
        await upload_file.close()
    return tmp_path
