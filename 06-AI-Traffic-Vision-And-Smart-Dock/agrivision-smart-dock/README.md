# AgriVision Smart Dock

AgriVision Smart Dock là một hệ thống hybrid tiên tiến kết hợp Trí tuệ nhân tạo (AI) và Công nghệ Blockchain để tự động hóa quy trình kiểm định chất lượng và thanh toán trong chuỗi cung ứng logistics dưa lưới.

## Tính năng chính
- **AI Quality Inspection**: Sử dụng mô hình YOLOv8 để tự động nhận diện và đánh giá chất lượng dưa lưới (kích thước, độ chín, khuyết tật).
- **Blockchain Automation**: Tích hợp mạng lưới Cardano để thực hiện các giao dịch thanh toán tự động (Smart Contracts) dựa trên kết quả kiểm định AI.
- **Real-time Dashboard**: Giao diện theo dõi trực quan cho phép quản lý kho và xem lịch sử giao dịch.

## Cấu trúc dự án
- `backend_server/`: Logic server xử lý dữ liệu và cơ sở dữ liệu SQLite.
- `ai_model_inference/`: Chứa mã nguồn thực thi mô hình AI YOLOv8.
- `blockchain_interact/`: Script tương tác với Cardano Testnet qua Blockfrost và pycardano.
- `frontend_dashboard/`: Giao diện người dùng Web-based để demo hệ thống.

## Công nghệ sử dụng
- **Backend**: Python FastAPI, SQLite
- **AI**: YOLOv8, OpenCV
- **Blockchain**: Cardano, PyCardano, Blockfrost API
- **Frontend**: HTML5, Vanilla CSS, JavaScript
