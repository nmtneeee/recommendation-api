import json
import re
import sqlite3

conn = sqlite3.connect("recs.db")
cursor = conn.cursor()

# 1. Lấy Ground Truth & Dùng Regex bóc tách tất cả mã số sản phẩm ra dạng chuẩn
cursor.execute("SELECT customer_id, actual_items FROM ground_truth")
gt_map = {}
for cid, actual_json in cursor.fetchall():
    cid_str = str(cid).strip()
    # Tìm tất cả chuỗi số (Item ID) nằm bên trong chuỗi text rác
    item_ids = re.findall(r"\b\d+\b", actual_json)
    if item_ids:
        gt_map[cid_str] = set(item_ids)

# 2. Lấy Recommendations & Tìm HIT
cursor.execute(
    "SELECT customer_id, has_history, item_ids FROM recommendations"
)
rec_rows = cursor.fetchall()

results = []
for cid, has_hist, rec_json in rec_rows:
    cid_str = str(cid).strip()
    if cid_str in gt_map:
        rec_items = set(str(x).strip() for x in json.loads(rec_json))
        actual_items = gt_map[cid_str]

        hits = rec_items.intersection(actual_items)
        if len(hits) > 0:
            results.append(
                (cid_str, has_hist, len(hits), len(actual_items), hits)
            )

# Sắp xếp theo số lượng HIT cao nhất
results.sort(key=lambda x: x[2], reverse=True)

print(
    f"\n🔥 TÌM THẤY {len(results)} BẢN GHI ĐOÁN TRÚNG (HIT > 0)! TOP 10 ID NÊN"
    " DÙNG:\n"
)
print("=" * 75)
print(
    f"{'Customer ID':<15} | {'Chế độ':<15} | {'Số HIT':<10} | Các SP đoán trúng"
)
print("=" * 75)

for cid, has_h, hit_c, total_act, hits in results[:10]:
    h_str = "Có lịch sử" if has_h == 1 else "Không lịch sử"
    print(
        f"{cid:<15} | {h_str:<15} | {hit_c}/10 món   | {list(hits)[:3]}"
    )

print("=" * 75)
conn.close()