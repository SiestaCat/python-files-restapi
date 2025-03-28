# Use an official lightweight Python image.
FROM python:3.9-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file and install dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Expose the port defined in your application (default is 8080).
EXPOSE 8080

# Run the application with uvicorn.
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]