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
   git clone https://your-repository-url.git
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
   API_KEY=your_api_key_here
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
- **Headers:** `X-API-Key: your_api_key_here`
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
- **Headers:** `X-API-Key: your_api_key_here`
- **Response:** Returns the requested file if it exists. Otherwise, responds with a 404 error.

## Curl Examples

### Upload Files

```bash
curl -X POST http://localhost:8080/upload \
  -H "X-API-Key: your_api_key_here" \
  -F "files=@/path/to/example.txt" \
  -F "files=@/path/to/image.png"
```

### Download File

```bash
curl -X GET http://localhost:8080/download/generated_upload_folder/example.txt \
  -H "X-API-Key: your_api_key_here" \
  --output example.txt
```

### Curl Examples in PowerShell (Windows)

When using PowerShell, it's recommended to call `curl.exe` to avoid conflicts with the alias for Invoke-WebRequest.

#### Upload Files

```powershell
curl.exe -X POST http://localhost:8080/upload `
  -H "X-API-Key: your_api_key_here" `
  -F "files=@C:\path\to\example.txt" `
  -F "files=@C:\path\to\image.png"
```

#### Download File

```powershell
curl.exe -X GET http://localhost:8080/download/generated_upload_folder/example.txt `
  -H "X-API-Key: your_api_key_here" `
  --output example.txt
```

*Replace `generated_upload_folder` with the actual folder name returned from the upload endpoint, and update `/path/to/your/file` accordingly.*

## Docker Usage

### Build the Docker Image

```bash
docker build -t python-files-api .
```

### Run the Docker Container

```bash
docker run -d -p 8000:8000 --env API_KEY=your_api_key_here python-files-api
```

*Note: Adjust the environment variables as needed.*

## Additional Information

- **File Storage:** Uploaded files are stored in the `files` directory. The server creates this directory if it does not exist.
- **Dependencies:** The application uses FastAPI, Uvicorn, and other required packages listed in `requirements.txt`.
- **Configuration:** Customize the port and API key via the `.env` file.