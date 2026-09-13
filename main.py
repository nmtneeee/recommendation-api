from fastapi import FastAPI, HTTPException
import sqlite3
import json

app = FastAPI(title="Recommendation System API")

def query_recommendation(customer_id: str, use_history: bool):
    has_hist = 1 if use_history else 0
    conn = sqlite3.connect("recs.db")
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT items FROM recommendations WHERE customer_id = ? AND has_history = ?",
        (customer_id, has_hist)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row[0])
    return None

@app.get("/recommend/{customer_id}")
def get_recommendation(customer_id: str, use_history: bool = True):
    items = query_recommendation(customer_id, use_history)
    if not items:
        raise HTTPException(status_code=404, detail="Không tìm thấy Customer ID")
        
    return {customer_id: items}