"""
Safe ZIP upload + extraction (spec sections 1, 33, 34).

Security rules enforced here, not left to caller discretion:
- reject non-ZIP files
- reject oversized uploads (both compressed and uncompressed-size limits --
  a small ZIP can still zip-bomb into gigabytes)
- reject any entry whose resolved path would escape the destination
  directory ("zip slip") -- checked BEFORE extraction, not after
- reject symlink entries
- never execute anything from the uploaded archive
- original upload is preserved untouched under workspace/original/;
  nothing else in the system is allowed to write there
"""
import zipfile
from pathlib import Path
from fastapi import UploadFile, HTTPException

MAX_UPLOAD_BYTES = 50 * 1024 * 1024        # 50 MB compressed
MAX_UNCOMPRESSED_BYTES = 500 * 1024 * 1024  # 500 MB total extracted
WORKSPACE_ROOT = Path("workspace")


def _validate_zip_entries(zf: zipfile.ZipFile, dest: Path) -> None:
    total_uncompressed = 0
    dest_resolved = dest.resolve()

    for info in zf.infolist():
        if info.is_dir():
            continue

        # zip slip check: resolved path must stay inside dest
        target = (dest / info.filename).resolve()
        if not str(target).startswith(str(dest_resolved)):
            raise HTTPException(status_code=400, detail=f"Unsafe path in archive: {info.filename}")

        # reject symlinks (external_attr high bits encode unix file mode)
        mode = info.external_attr >> 16
        if mode and (mode & 0o170000) == 0o120000:
            raise HTTPException(status_code=400, detail=f"Symlinks not allowed in archive: {info.filename}")

        total_uncompressed += info.file_size
        if total_uncompressed > MAX_UNCOMPRESSED_BYTES:
            raise HTTPException(status_code=400, detail="Archive exceeds maximum uncompressed size")


def extract_project_zip(upload: UploadFile, project_id: str) -> Path:
    if not upload.filename or not upload.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are accepted")

    dest = WORKSPACE_ROOT / "original" / project_id
    dest.mkdir(parents=True, exist_ok=True)

    tmp_path = WORKSPACE_ROOT / f"_upload_{project_id}.zip"
    tmp_path.parent.mkdir(parents=True, exist_ok=True)

    size = 0
    with open(tmp_path, "wb") as out:
        while chunk := upload.file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                tmp_path.unlink(missing_ok=True)
                raise HTTPException(status_code=400, detail="Upload exceeds maximum allowed size (50MB)")
            out.write(chunk)

    try:
        with zipfile.ZipFile(tmp_path) as zf:
            _validate_zip_entries(zf, dest)
            zf.extractall(dest)  # safe now -- every entry validated above
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="File is not a valid ZIP archive")
    finally:
        tmp_path.unlink(missing_ok=True)

    return dest
