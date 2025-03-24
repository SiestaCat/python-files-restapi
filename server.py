import os
import uuid
import shutil
import mimetypes
from typing import List

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Depends
from fastapi.responses import FileResponse, HTMLResponse
from starlette.status import HTTP_401_UNAUTHORIZED

# Attempt to load environment variables from a .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Retrieve the API key and port from environment variables
API_KEY = os.getenv("API_KEY", "default_api_key")
PORT = int(os.getenv("HTTP_SERVER_PORT", "8000"))

# Define the base directory to store files
FILES_DIR = "files"

app = FastAPI()

# Create the "files" directory if it doesn't exist
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

# Dependency to verify API key via request headers (expects header "X-API-Key")
async def verify_api_key(request: Request):
    header_api_key = request.headers.get("X-API-Key")
    if header_api_key != API_KEY:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

# Download endpoint: stream file download from the "files" directory
@app.get("/download/{file_path:path}")
async def download_file(file_path: str, request: Request, api_key: None = Depends(verify_api_key)):
    full_path = os.path.join(FILES_DIR, file_path)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    # Auto-detect mime type; default to octet-stream if undetermined
    mime_type, _ = mimetypes.guess_type(full_path)
    if mime_type is None:
        mime_type = "application/octet-stream"
    # FileResponse streams the file without loading the entire file into memory
    return FileResponse(full_path, media_type=mime_type, filename=os.path.basename(full_path))

# Upload endpoint: allow single or multiple file uploads
@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    request: Request = None,
    api_key: None = Depends(verify_api_key)
):
    # Create a unique UUID folder for this upload session
    unique_folder = os.path.join(FILES_DIR, str(uuid.uuid4()))
    os.makedirs(unique_folder, exist_ok=True)
    saved_files = []
    for file in files:
        file_path = os.path.join(unique_folder, file.filename)
        # Stream the file content to disk to support large files without high memory usage
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_files.append(file.filename)
    return {"folder": os.path.basename(unique_folder), "files": saved_files}

# Stats endpoint: returns the "stats.html" file as an HTML response
@app.get("/stats", response_class=HTMLResponse)
async def get_stats():
    return FileResponse("stats.html", media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    # Run the app with plain HTTP on the port specified in the environment
    uvicorn.run(app, host="0.0.0.0", port=PORT)
