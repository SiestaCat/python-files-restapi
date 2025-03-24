import os
import uuid
import shutil
import mimetypes
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

# Retrieve the API key from environment variables
API_KEY = os.getenv("API_KEY", "default_api_key")

# Define the base directory to store files
FILES_DIR = "files"

app = FastAPI()

templates = Jinja2Templates(directory="templates")

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
    mime_type, _ = mimetypes.guess_type(full_path)
    if mime_type is None:
        mime_type = "application/octet-stream"
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
    saved_files = []
    for file in files:
        file_path = os.path.join(unique_folder, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_files.append(file.filename)
    return {"folder": os.path.basename(unique_folder), "files": saved_files}

# Template endpoint: returns the stats page with default port passed in
@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    return templates.TemplateResponse("stats.html", {"request": request, "port": 8080})

@app.get("/getstats")
async def get_file_stats(api_key: None = Depends(verify_api_key)):
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

    total_size_gb = total_size / (1024**3)
    size_str = f"{total_size_gb:.2f}".replace('.', ',') + " GB"
    
    return {"folders": total_folders, "files": total_files, "size": size_str}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
