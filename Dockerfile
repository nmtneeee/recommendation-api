# Sử dụng image Python gọn nhẹ
FROM python:3.9-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy các file cần thiết vào container
COPY requirements.txt .
COPY main.py .
COPY withhist_predictions.json .
COPY predictions_without_history.json .

# Cài đặt thư viện
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Lệnh chạy API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]