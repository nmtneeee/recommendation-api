import json
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="Recommendation System API")

# Nhúng trực tiếp giao diện Web UI vào biến Python
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo Recommendation System</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 min-h-screen p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <div class="bg-white rounded-2xl shadow-sm p-6 mb-6 border border-slate-200">
            <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-2">
                🛍️ Hệ Thống Gợi Ý Sản Phẩm (Recommendation System)
            </h1>
            <p class="text-slate-500 text-sm mt-1">Đồ án CS116 - Tra cứu Top 10 sản phẩm gợi ý theo Customer ID</p>
            
            <div class="mt-6 flex flex-col md:flex-row gap-4 items-end">
                <div class="flex-1 w-full">
                    <label class="block text-sm font-semibold text-slate-700 mb-1">Mã khách hàng (Customer ID)</label>
                    <input type="text" id="cusId" value="17212" placeholder="Nhập Customer ID..." 
                           class="w-full px-4 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none">
                </div>
                <div class="w-full md:w-48">
                    <label class="block text-sm font-semibold text-slate-700 mb-1">Sử dụng lịch sử</label>
                    <select id="useHistory" class="w-full px-4 py-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none">
                        <option value="true">Có (With History)</option>
                        <option value="false">Không (No History)</option>
                    </select>
                </div>
                <button onclick="fetchRecommendations()" 
                        class="w-full md:w-auto bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-6 py-2.5 rounded-xl transition duration-200">
                    🔍 Xem Gợi Ý
                </button>
            </div>
        </div>

        <!-- Thống kê Hit/Miss -->
        <div id="statsContainer" class="hidden mb-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <div class="text-slate-500 text-xs">Tổng sản phẩm</div>
                <div class="text-xl font-bold text-slate-800" id="totalItems">10</div>
            </div>
            <div class="bg-emerald-50 p-4 rounded-xl border border-emerald-200 shadow-sm">
                <div class="text-emerald-600 text-xs font-semibold">Đoán Đúng (HIT)</div>
                <div class="text-xl font-bold text-emerald-700" id="hitCount">0</div>
            </div>
            <div class="bg-rose-50 p-4 rounded-xl border border-rose-200 shadow-sm">
                <div class="text-rose-600 text-xs font-semibold">Đoán Sai (MISS)</div>
                <div class="text-xl font-bold text-rose-700" id="missCount">0</div>
            </div>
            <div class="bg-indigo-50 p-4 rounded-xl border border-indigo-200 shadow-sm">
                <div class="text-indigo-600 text-xs font-semibold">Tỷ lệ Hit Rate @10</div>
                <div class="text-xl font-bold text-indigo-700" id="hitRate">0%</div>
            </div>
        </div>

        <!-- Khung danh sách sản phẩm -->
        <div id="loading" class="hidden text-center py-12 text-slate-500">⏳ Đang tải dữ liệu gợi ý...</div>
        <div id="error" class="hidden bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-xl mb-6"></div>
        <div id="gridResults" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
    </div>

    <script>
        async function fetchRecommendations() {
            const cusId = document.getElementById('cusId').value.trim();
            const useHistory = document.getElementById('useHistory').value;
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const grid = document.getElementById('gridResults');
            const stats = document.getElementById('statsContainer');

            if (!cusId) return alert('Vui lòng nhập Customer ID');

            loading.classList.remove('hidden');
            error.classList.add('hidden');
            grid.innerHTML = '';

            try {
                const res = await fetch(`/recommend/${cusId}?use_history=${useHistory}`);
                if (!res.ok) throw new Error('Không tìm thấy dữ liệu cho Customer ID này!');
                
                const data = await res.json();
                const items = data.recommendations;

                let hits = 0;
                items.forEach(i => { if (i.is_hit) hits++; });
                
                document.getElementById('totalItems').innerText = items.length;
                document.getElementById('hitCount').innerText = hits;
                document.getElementById('missCount').innerText = items.length - hits;
                document.getElementById('hitRate').innerText = ((hits / items.length) * 100).toFixed(0) + '%';
                stats.classList.remove('hidden');

                items.forEach((item, index) => {
                    const isHit = item.is_hit;
                    const badgeClass = isHit ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'bg-rose-100 text-rose-800 border-rose-300';
                    const formattedPrice = item.price ? item.price.toLocaleString('vi-VN') + ' đ' : 'Liên hệ';

                    grid.innerHTML += `
                        <div class="bg-white rounded-xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition relative flex flex-col justify-between">
                            <div>
                                <div class="flex justify-between items-start mb-2">
                                    <span class="text-xs font-bold text-slate-400">#${index + 1}</span>
                                    <span class="px-2.5 py-0.5 text-xs font-bold rounded-full border ${badgeClass}">
                                        ${item.status}
                                    </span>
                                </div>
                                <div class="text-xs font-semibold text-indigo-600 uppercase tracking-wide mb-1">${item.brand}</div>
                                <h3 class="font-bold text-slate-800 text-sm mb-2 line-clamp-2">ID: ${item.item_id}</h3>
                                <div class="text-xs text-slate-500 mb-1">📁 ${item.category_l1} &gt; ${item.category_l2}</div>
                            </div>
                            <div class="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center">
                                <span class="text-xs text-slate-400">Giá tham khảo:</span>
                                <span class="text-base font-bold text-slate-900">${formattedPrice}</span>
                            </div>
                        </div>
                    `;
                });

            } catch (err) {
                error.innerText = err.message;
                error.classList.remove('hidden');
                stats.classList.add('hidden');
            } finally {
                loading.classList.add('hidden');
            }
        }
        fetchRecommendations();
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def read_index():
    return HTMLResponse(content=HTML_CONTENT)


@app.get("/recommend/{customer_id}")
def get_recommendation(customer_id: str, use_history: bool = True):
    has_hist = 1 if use_history else 0
    conn = sqlite3.connect("recs.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT item_ids FROM recommendations WHERE customer_id = ? AND"
        " has_history = ?",
        (customer_id, has_hist),
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(
            status_code=404, detail="Không tìm thấy Customer ID"
        )

    rec_item_ids = json.loads(row[0])

    cursor.execute(
        "SELECT actual_items FROM ground_truth WHERE customer_id = ?",
        (customer_id,),
    )
    gt_row = cursor.fetchone()
    actual_set = set(json.loads(gt_row[0])) if gt_row else set()

    placeholders = ",".join(["?"] * len(rec_item_ids))
    cursor.execute(
        f"SELECT item_id, brand, category_l1, category_l2, price FROM items"
        f" WHERE item_id IN ({placeholders})",
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