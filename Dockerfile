FROM python:3.12-slim

# Set up system directories
WORKDIR /code

# Copy python dependency list
COPY backend/requirements.txt /code/requirements.txt

# Install packages
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy entire backend source code
COPY backend /code/backend

# Configure Python path and default variables
ENV PYTHONPATH=/code/backend
ENV DATABASE_URL=sqlite:////code/backend/studentcareer.db
ENV ENV=development
ENV PORT=7860

# Create writable storage directory for the ML model
RUN mkdir -p /code/backend/storage && chmod 777 /code/backend/storage

# Expose Hugging Face Space port
EXPOSE 7860

# Start Uvicorn pointing to backend/app/main.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
