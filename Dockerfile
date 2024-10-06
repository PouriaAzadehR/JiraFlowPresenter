# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory for the app
WORKDIR /app

# Copy the backend and frontend directories to the container
COPY backend /app/backend
COPY frontend /app/frontend

# Install Python dependencies for the backend
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Expose ports for both Flask (5000) and HTTP server (8000)
EXPOSE 5000
EXPOSE 8000

# Install Supervisor to manage multiple processes
RUN apt-get update && apt-get install -y supervisor

# Copy the Supervisor configuration file
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Command to start Supervisor, which in turn starts both Flask and the HTTP server
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]