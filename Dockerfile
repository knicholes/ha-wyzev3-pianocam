# Stage 1: Build stage
FROM python:3.9-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from the builder
COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

# Set the working directory in the container
WORKDIR /app

# Copy the rest of the application code into the container
COPY . .

# Command to run the application
CMD ["python", "main.py"]
