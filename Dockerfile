FROM python:3.11-slim

# Install FFmpeg (required for audio processing)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend files
COPY backend/requirements.txt ./
COPY backend/main.py ./
COPY backend/studio-room-tone.wav ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend to serve static files
COPY frontend/ ./frontend/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
