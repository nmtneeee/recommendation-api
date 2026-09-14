from fastapi import FastAPI, HTTPException
import json
import sqlite3

app = FastAPI(title="Recommendation System API")


@app.get("/recommend/{customer_id}")
def get_recommendation(customer_id: str, use_history: bool = True):
    has_hist = 1 if use_history else 0
    conn = sqlite3.connect("recs.db")
    cursor = conn.cursor()

    # 1. Lấy danh sách 10 ID sản phẩm dự đoán
    cursor.execute(
        "SELECT item_ids FROM recommendations WHERE customer_id = ? AND has_history = ?",
        (customer_id, has_hist),
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(
            status_code=404, detail="Không tìm thấy Customer ID"
        )

    rec_item_ids = json.loads(row[0])

    # 2. Lấy danh sách sản phẩm thực tế khách đã mua (Ground Truth)
    cursor.execute(
        "SELECT actual_items FROM ground_truth WHERE customer_id = ?",
        (customer_id,),
    )
    gt_row = cursor.fetchone()
    actual_set = set(json.loads(gt_row[0])) if gt_row else set()

    # 3. Lấy thông tin chi tiết tên, giá, brand từ bảng items
    placeholders = ",".join(["?"] * len(rec_item_ids))
    cursor.execute(
        f"SELECT item_id, brand, category_l1, category_l2, price FROM items WHERE item_id IN ({placeholders})",
        rec_item_ids,
    )
    item_rows = cursor.fetchall()

    item_info_map = {
        r[0]: {
            "item_id": r[0],
            "brand": r[1],
            "category_l1": r[2],
            "category_l2": r[3],
            "price": r[4],
        }
        for r in item_rows
    }
    conn.close()

    # 4. Kết hợp dữ liệu và gắn nhãn HIT / MISS
    results = []
    for i_id in rec_item_ids:
        info = item_info_map.get(
            i_id,
            {
                "item_id": i_id,
                "brand": "N/A",
                "category_l1": "N/A",
                "category_l2": "N/A",
                "price": 0.0,
            },
        ).copy()
        is_hit = i_id in actual_set
        info["is_hit"] = is_hit
        info["status"] = "HIT" if is_hit else "MISS"
        results.append(info)

    return {"customer_id": customer_id, "recommendations": results}