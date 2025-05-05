
# Use Python 3.13.1 as base image
FROM python:3.13.1-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a directory for persistent data
RUN mkdir -p /app/data
RUN mkdir -p /app/src/content

# Copy the Python script
COPY rip_jobs.py .

# Set the data directory as a volume
# VOLUME ["/app/data"]
# already in the docker-compose.yml

# Command to run when container starts
CMD ["python", "rip_jobs.py"]
