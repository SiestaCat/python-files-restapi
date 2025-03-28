# Python Files API

A simple FastAPI service for uploading and downloading files with API key protection.

## Features

- **File Uploads**: Supports single or multiple file uploads.
- **File Downloads**: Streams file downloads from the server.
- **API Key Security**: Endpoints are protected via an API key.

## Prerequisites

- Python 3.9+
- pip
- Docker (optional, for containerized deployment)

## Installation

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SiestaCat/python-files-restapi.git
   cd python-files-api
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # For Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   Create a `.env` file in the project root with the following content:

   ```properties
   API_KEY=changeme
   HTTP_SERVER_PORT=8080
   ```

### Running Locally

Start the server with:
```bash
python server.py
```
Your API will be available at: `http://localhost:8080`

## API Endpoints

### Upload Files

- **Endpoint:** `/upload`
- **Method:** `POST`
- **Headers:** `X-API-Key: changeme`
- **Form Data:** Upload files using the key `files`
- **Response Example:**
  ```json
  {
      "folder": "generated_upload_folder",
      "files": ["example.txt", "image.png"]
  }
  ```

### Download File

- **Endpoint:** `/download/{file_path}`
- **Method:** `GET`
- **Headers:** `X-API-Key: changeme`
- **Response:** Returns the requested file if it exists. Otherwise, responds with a 404 error.

## Curl Examples

### Upload Files

```bash
curl -X POST http://localhost:8080/upload \
  -H "X-API-Key: changeme" \
  -F "files=@/path/to/example.txt" \
  -F "files=@/path/to/image.png"
```

### Download File

```bash
curl -X GET http://localhost:8080/download/generated_upload_folder/example.txt \
  -H "X-API-Key: changeme" \
  --output example.txt
```

### Curl Examples in PowerShell (Windows)

When using PowerShell, it's recommended to call `curl.exe` to avoid conflicts with the alias for Invoke-WebRequest.

#### Upload Files

```powershell
curl.exe -X POST http://localhost:8080/upload `
  -H "X-API-Key: changeme" `
  -F "files=@C:\path\to\example.txt" `
  -F "files=@C:\path\to\image.png"
```

#### Download File

```powershell
curl.exe -X GET http://localhost:8080/download/generated_upload_folder/example.txt `
  -H "X-API-Key: changeme" `
  --output example.txt
```

*Replace `generated_upload_folder` with the actual folder name returned from the upload endpoint, and update `/path/to/your/file` accordingly.*

## Docker Usage

### Build the Docker Image

```bash
docker build --progress=plain -t python-files-api .
```

### One-Click Deployment with Dockerfile-oneclick

If you prefer a one-click setup using the provided Dockerfile-oneclick, run:

```bash
docker build --progress=plain -f Dockerfile-oneclick -t python-files-api .
```

### Run the Docker Container

```bash
docker run --rm -it -p 8080:8080 --env API_KEY=changeme python-files-api
```

*Remember to update the API key and port as needed.*

### Run the Docker Container with Persistent Storage

To ensure that uploaded files persist between container runs, mount the local "files" folder as a Docker volume:

```bash
docker run --rm -it -p 8080:8080 -v .\files:/files --env API_KEY=changeme python-files-api
```

## Additional Information

- **File Storage:** Uploaded files are stored in the `files` directory. The server creates this directory if it does not exist.
- **Dependencies:** The application uses FastAPI, Uvicorn, and other required packages listed in `requirements.txt`.
- **Configuration:** Customize the port and API key via the `.env` file.