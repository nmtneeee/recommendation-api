import json
import sqlite3

# Kết nối (hoặc tạo mới) file cơ sở dữ liệu recs.db
conn = sqlite3.connect("recs.db")
cursor = conn.cursor()

# Tạo bảng chứa dữ liệu
cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        customer_id TEXT,
        has_history INTEGER,
        items TEXT,
        PRIMARY KEY (customer_id, has_history)
    )
""")

def insert_data(file_path, has_history_flag):
    print(f"Đang xử lý file {file_path}...")
    with open(file_path, "r") as f:
        data = json.load(f)
        
    records = []
    for cus_id, items in data.items():
        # Chỉ lưu top 10 món hàng dưới dạng chuỗi JSON
        records.append((cus_id, has_history_flag, json.dumps(items[:10])))
        
    cursor.executemany(
        "INSERT OR REPLACE INTO recommendations VALUES (?, ?, ?)", records
    )
    conn.commit()

# Đưa dữ liệu từ 2 file JSON vào SQLite
insert_data("withhist_predictions.json", 1)
insert_data("predictions_without_history.json", 0)

conn.close()
print("Thành công! File recs.db đã được tạo.")