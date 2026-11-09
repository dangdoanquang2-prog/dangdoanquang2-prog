from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import sys
import os
import shutil

# Thêm thư mục gốc vào path để import các module khác
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_model_inference.inference import run_mock_inference
from blockchain_interact.cardano_wallet import create_cip20_hash, mock_submit_transaction

app = FastAPI(title="AgriVision Smart Dock API")

# Cấu hình CORS để Frontend (chạy ở port khác hoặc mở file local) có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "inventory.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT UNIQUE,
            total_weight REAL,
            type_1_weight REAL,
            bad_weight REAL,
            tx_hash TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to AgriVision Smart Dock API"}

@app.post("/api/scan-shipment")
async def scan_shipment(
    batch_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Endpoint chính xử lý luồng vận hành tại Dock. Nhận file ảnh từ người dùng.
    """
    # 1. Lưu file ảnh vào thư mục tạm
    temp_image_path = f"temp_{batch_id}_{file.filename}"
    with open(temp_image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Gọi AI (The Physical Edge) với file ảnh thật
    ai_result = run_mock_inference(batch_id, temp_image_path)
    
    # 3. Băm dữ liệu & Đưa lên Blockchain giả lập (The Web3 Trust)
    data_hash = create_cip20_hash(ai_result)
    tx_id = mock_submit_transaction(data_hash)
    
    # 4. Lưu vào Database (The System Brain)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO inventory (batch_id, total_weight, type_1_weight, bad_weight, tx_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (ai_result['batch_id'], ai_result['total_weight'], ai_result['type_1'], ai_result['bad_quality'], tx_id))
        conn.commit()
    except sqlite3.IntegrityError:
        return {"error": "Lô hàng (Batch ID) này đã được quét và tồn tại trong hệ thống."}
    finally:
        conn.close()
        
    return {
        "message": "Quét và lưu thành công",
        "ai_data": ai_result,
        "blockchain_tx": tx_id
    }

@app.get("/inventory")
def get_inventory():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inventory ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return {"items": [dict(row) for row in rows]}
