FROM python:3.9-slim

WORKDIR /app

# Cài đặt thư viện ứng dụng và gdown để tải file từ Google Drive
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gdown

# Tải file recs.db trực tiếp từ Google Drive vào container trong lúc build

RUN gdown --id 18-ua_7zGgruV3mOx7yHSwOT4n2SfTQGP -O recs.db

# Copy code FastAPI vào
COPY main.py .
COPY index.html .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]