import json
import pickle
import re  
import pandas as pd
import sqlite3

conn = sqlite3.connect("recs.db")
cursor = conn.cursor()

# 1. BẢNG ITEMS
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
            str(row["item_id"]).strip(),
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

# 2. BẢNG GROUND TRUTH (Làm sạch Numpy Array & Chuỗi rác)
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


def clean_item_list(items_obj):
    if isinstance(items_obj, str):
        return re.findall(r"\b\d+\b", items_obj)
    try:
        flat = []
        for x in items_obj:
            if isinstance(x, str) and ("[" in x or " " in x):
                flat.extend(re.findall(r"\b\d+\b", x))
            else:
                flat.append(str(x).strip())
        return flat
    except TypeError:
        return [str(items_obj).strip()]


if isinstance(raw_gt, dict):
    for cus_id, items in raw_gt.items():
        gt_records.append(
            (str(cus_id).strip(), json.dumps(clean_item_list(items)))
        )
elif isinstance(raw_gt, pd.Series):
    for cus_id, items in raw_gt.items():
        gt_records.append(
            (str(cus_id).strip(), json.dumps(clean_item_list(items)))
        )
elif isinstance(raw_gt, pd.DataFrame):
    cols = raw_gt.columns
    grouped = raw_gt.groupby(cols[0])[cols[1]].apply(list)
    for cus_id, items in grouped.items():
        gt_records.append(
            (str(cus_id).strip(), json.dumps(clean_item_list(items)))
        )

cursor.executemany(
    "INSERT OR REPLACE INTO ground_truth VALUES (?, ?)", gt_records
)
print(f"   -> Đã chèn {len(gt_records)} khách hàng vào bảng ground_truth.")

# 3. BẢNG RECOMMENDATIONS
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
        (
            str(cus_id).strip(),
            has_hist_flag,
            json.dumps([str(i).strip() for i in items[:10]]),
        )
        for cus_id, items in data.items()
    ]
    cursor.executemany(
        "INSERT OR REPLACE INTO recommendations VALUES (?, ?, ?)", records
    )


insert_recs("withhist_predictions.json", 1)
insert_recs("predictions_without_history.json", 0)

# 4. LƯU THẮNG VÀO DISK & ĐÓNG KẾT NỐI
conn.commit()
conn.close()
print(" THÀNH CÔNG! ")