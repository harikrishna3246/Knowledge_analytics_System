FROM python:3.11.8-slim

WORKDIR /app

# Upgrade pip, setuptools, and wheel for better wheel support
RUN pip install --upgrade pip setuptools wheel

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
COPY backend/download_nltk_data.py .
RUN python download_nltk_data.py

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]