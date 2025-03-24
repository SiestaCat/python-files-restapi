import os
import uuid
import shutil
import mimetypes
import logging     # added import for logging
from typing import List

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Depends
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_401_UNAUTHORIZED

# Attempt to load environment variables from a .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Retrieve the API key from environment variables
API_KEY = os.getenv("API_KEY", "default_api_key")

# Define base directory to store files
FILES_DIR = "files"

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Create the "files" directory if it doesn't exist
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)
    logger.info(f"Created files directory at {FILES_DIR}")

# Dependency to verify API key via request headers (expects header "X-API-Key")
async def verify_api_key(request: Request):
    header_api_key = request.headers.get("X-API-Key")
    if header_api_key != API_KEY:
        logger.warning("Unauthorized access attempt with invalid API key")
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    logger.info("API key verification successful")
    
# Download endpoint: stream file download from the "files" directory
@app.get("/download/{file_path:path}")
async def download_file(file_path: str, request: Request, api_key: None = Depends(verify_api_key)):
    full_path = os.path.join(FILES_DIR, file_path)
    if not os.path.isfile(full_path):
        logger.error(f"File not found: {full_path}")
        raise HTTPException(status_code=404, detail="File not found")
    mime_type, _ = mimetypes.guess_type(full_path)
    if mime_type is None:
        mime_type = "application/octet-stream"
    logger.info(f"Downloading file: {full_path}")
    return FileResponse(full_path, media_type=mime_type, filename=os.path.basename(full_path))

# Upload endpoint: allow single or multiple file uploads
@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    request: Request = None,
    api_key: None = Depends(verify_api_key)
):
    unique_folder = os.path.join(FILES_DIR, str(uuid.uuid4()))
    os.makedirs(unique_folder, exist_ok=True)
    logger.info(f"Created unique upload folder: {unique_folder}")
    saved_files = []
    total_upload_size = 0
    for file in files:
        file_path = os.path.join(unique_folder, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_size = os.path.getsize(file_path)
        total_upload_size += file_size
        saved_files.append({
            "filename": file.filename,
            "size_bytes": file_size,
            "size_formatted": format_size(file_size)
        })
        logger.info(f"Uploaded file: {file.filename} ({format_size(file_size)}) to {unique_folder}")
    
    # Log the formatted total upload size
    formatted_total_size = format_size(total_upload_size)
    logger.info(f"Total uploaded size: {formatted_total_size} ({total_upload_size} bytes)")
    
    return {
        "folder": os.path.basename(unique_folder),
        "files": saved_files,
        "total_upload_size_bytes": total_upload_size,
        "total_upload_size_formatted": formatted_total_size
    }

# Template endpoint merged with getstats functionality:
@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    total_folders = 0
    total_files = 0
    total_size = 0

    for root, dirs, files in os.walk(FILES_DIR):
        total_folders += len(dirs)
        total_files += len(files)
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)

    size_str = format_size(total_size)
    logger.info(f"Stats calculated: {total_folders} folders, {total_files} files, total size {size_str}")
    return templates.TemplateResponse("stats.html", {
        "request": request,
        "folders": total_folders,
        "files": total_files,
        "size": size_str
    })

def format_size(size_bytes):
    # Returns size formatted in B, KB, MB, GB, TB, or PT
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PT"]
    size = float(size_bytes)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PT"

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
