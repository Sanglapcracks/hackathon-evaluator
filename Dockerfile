FROM python:3.10

WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose correct port for HF Spaces
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]