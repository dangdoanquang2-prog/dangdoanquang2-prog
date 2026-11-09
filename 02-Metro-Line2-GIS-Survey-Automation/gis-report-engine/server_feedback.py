import os, sys, json
from http.server import HTTPServer, SimpleHTTPRequestHandler

sys.stdout.reconfigure(encoding='utf-8')

HOST = '127.0.0.1'
PORT = 8088
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class FeedbackServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/save':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # Lưu file JSON
                json_path = os.path.join(DIRECTORY, 's23_user_feedback.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # Lưu thêm file Markdown dễ đọc
                md_path = os.path.join(DIRECTORY, 's23_user_feedback.md')
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write("# GHI CHÚ VÀ YÊU CẦU CHỈNH SỬA TỪ NGƯỜI DÙNG\n\n")
                    f.write(f"- **Thời gian lưu:** {data.get('saved_at', 'Chưa rõ')}\n")
                    f.write(f"- **Nhà ga:** {data.get('station', 'Ga S23 - Ba Sa')}\n\n")
                    f.write("## 1. Các ghi chú theo từng Mục\n\n")
                    notes = data.get('notes', {})
                    has_note = False
                    for sec_id, note_text in notes.items():
                        if note_text and note_text.strip():
                            has_note = True
                            f.write(f"### {sec_id}\n")
                            f.write(f"{note_text.strip()}\n\n")
                    if not has_note:
                        f.write("_Không có ghi chú thêm ở các ô mục._\n\n")
                    
                    edited_texts = data.get('edited_texts', {})
                    if edited_texts:
                        f.write("## 2. Các đoạn văn đã sửa trực tiếp trên văn bản\n\n")
                        for element_id, text in edited_texts.items():
                            f.write(f"- **Phần tử [{element_id}]:** {text.strip()}\n")

                print(f"[+] Đã nhận và lưu phản hồi thành công vào: {json_path} & {md_path}")

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {
                    'status': 'success',
                    'message': 'Đã lưu phản hồi thành công vào workspace!',
                    'file': 's23_user_feedback.json'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                print(f"[-] Lỗi khi xử lý POST /api/save: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, FeedbackServerHandler)
    print(f"[*] Local Feedback Server đang chạy tại: http://{HOST}:{PORT}/")
    print(f"[*] Mở xem báo cáo tương tác tại: http://{HOST}:{PORT}/BaoCao_KhaoSat_ThucDia_Ga_S23_BaSa_XemTruoc.html")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
