FROM python:3.9-slim

WORKDIR /app

# Cài đặt thư viện ứng dụng và gdown để tải file từ Google Drive
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gdown

# Tải file recs.db trực tiếp từ Google Drive vào container trong lúc build
# Thay YOUR_FILE_ID_HERE bằng ID lấy từ bước 1 (giữ nguyên cờ -O recs.db)
RUN gdown --id 152sulK5YR0UTiBI8OPz0hcoJUIrmYumV -O recs.db

# Copy code FastAPI vào
COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]