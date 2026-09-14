import json
import pickle
import pandas as pd
import sqlite3

conn = sqlite3.connect("recs.db")
cursor = conn.cursor()

# 1. BẢNG ITEMS (Lưu thông tin sản phẩm, mỗi item_id chỉ 1 dòng)
print("1. Tạo bảng items...")
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS items (
        item_id TEXT PRIMARY KEY,
        brand TEXT,
        category_l1 TEXT,
        category_l2 TEXT,
        price REAL
    )
"""
)

items_df = pd.read_parquet("items.parquet")
items_records = []
for _, row in items_df.iterrows():
    items_records.append(
        (
            str(row["item_id"]),
            str(row["brand"]) if pd.notna(row.get("brand")) else "N/A",
            str(row["category_l1"])
            if pd.notna(row.get("category_l1"))
            else "",
            str(row["category_l2"])
            if pd.notna(row.get("category_l2"))
            else "",
            float(row["price"]) if pd.notna(row.get("price")) else 0.0,
        )
    )
cursor.executemany(
    "INSERT OR REPLACE INTO items VALUES (?, ?, ?, ?, ?)", items_records
)

# 2. BẢNG GROUND TRUTH (Lưu danh sách mua thực tế của customer)
print("2. Tạo bảng ground_truth...")
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS ground_truth (
        customer_id TEXT PRIMARY KEY,
        actual_items TEXT
    )
"""
)

with open("final_groundtruth.pkl", "rb") as f:
    raw_gt = pickle.load(f)

gt_records = []
if isinstance(raw_gt, dict):
    for cus_id, items in raw_gt.items():
        item_list = (
            [str(i) for i in items]
            if isinstance(items, (list, set, tuple))
            else [str(items)]
        )
        gt_records.append((str(cus_id), json.dumps(item_list)))
elif isinstance(raw_gt, (pd.DataFrame, pd.Series)):
    for cus_id, items in raw_gt.items():
        item_list = (
            [str(i) for i in items]
            if isinstance(items, (list, set, tuple))
            else [str(items)]
        )
        gt_records.append((str(cus_id), json.dumps(item_list)))

cursor.executemany(
    "INSERT OR REPLACE INTO ground_truth VALUES (?, ?)", gt_records
)

# 3. BẢNG RECOMMENDATIONS (Chỉ lưu 10 ID sản phẩm)
print("3. Tạo bảng recommendations...")
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS recommendations (
        customer_id TEXT,
        has_history INTEGER,
        item_ids TEXT,
        PRIMARY KEY (customer_id, has_history)
    )
"""
)


def insert_recs(file_path, has_hist_flag):
    print(f"Đang xử lý {file_path}...")
    with open(file_path, "r") as f:
        data = json.load(f)

    records = [
        (str(cus_id), has_hist_flag, json.dumps([str(i) for i in items[:10]]))
        for cus_id, items in data.items()
    ]
    cursor.executemany(
        "INSERT OR REPLACE INTO recommendations VALUES (?, ?, ?)", records
    )


insert_recs("withhist_predictions.json", 1)
insert_recs("predictions_without_history.json", 0)

conn.commit()
conn.close()
print(" THÀNH CÔNG! ")