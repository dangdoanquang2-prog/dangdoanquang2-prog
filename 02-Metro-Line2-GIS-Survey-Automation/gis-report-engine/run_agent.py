import os
import sys
import json
import docx
import google.generativeai as genai
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from pptx import Presentation
from pptx.util import Inches
from dotenv import load_dotenv

load_dotenv()

def get_station_info(st_id):
    try:
        with open("stations_db.json", "r", encoding="utf-8") as f:
            db = json.load(f)
            return db.get(st_id, "Unknown Station")
    except:
        return "Unknown Station"

def read_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def generate_ai_text(raw_text):
    prompt = f"""Bạn là một chuyên gia lập báo cáo dự án đường sắt đô thị. 
Dựa vào ghi chú thô sau của nhân viên khảo sát:
"{raw_text}"

Hãy viết lại thành một bài báo cáo trang trọng, học thuật (khoảng 10-15 dòng) để dán vào tài liệu chính thức. 
Trình bày rõ ràng các ý: Thông tin chung, Đánh giá lối đi, Đánh giá rào cản/bãi xe, Cảnh báo giao thông. 
Không dùng định dạng markdown hoa mỹ, chỉ viết text thuần, dùng bullet point (-)."""
    
    models_to_try = ['gemini-3.7-flash', 'gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-1.5-flash-latest']
    
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
    
    for m_name in models_to_try:
        try:
            model = genai.GenerativeModel(m_name)
            resp = model.generate_content(prompt)
            return resp.text
        except Exception as e:
            continue
            
    return "(LỖI AI: Không gọi được API. Đây là bản raw:)\n" + raw_text

def run_agent(st_id):
    data_dir = os.path.join("data", st_id)
    if not os.path.exists(data_dir):
        print(f"Error: Folder {data_dir} does not exist.")
        return

    st_name = get_station_info(st_id)
    print(f"--- AGENT ĐANG XỬ LÝ GA: {st_id} - {st_name} ---")

    # 1. Đọc ghi chú
    note_path = os.path.join(data_dir, "ghichu.docx")
    raw_text = ""
    if os.path.exists(note_path):
        print("[1/5] Đang đọc file ghichu.docx...")
        raw_text = read_docx(note_path)
    else:
        print("[1/5] CẢNH BÁO: Không tìm thấy ghichu.docx")

    # 2. Sinh văn bản AI
    print("[2/5] Đang gọi Gemini AI để viết báo cáo...")
    ai_result = generate_ai_text(raw_text)

    # Lấy danh sách toàn bộ ảnh trong thư mục (trừ docx/txt)
    print("[3/5] Đang quét và lắp ráp ảnh...")
    tpl = DocxTemplate("Template_BaoCao_V3.docx")
    all_files = [f for f in os.listdir(data_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    def get_img(slot_name, width_mm=50):
        # Nếu có file đúng tên thì dùng
        path = os.path.join(data_dir, slot_name)
        if os.path.exists(path):
            return InlineImage(tpl, path, width=Mm(width_mm))
        # Nếu không có, lấy bừa 1 ảnh từ mảng (nếu còn)
        elif len(all_files) > 0:
            random_img = all_files.pop(0)
            return InlineImage(tpl, os.path.join(data_dir, random_img), width=Mm(width_mm))
        return ""

    context = {
        "TEN_GA_UPPER": st_name.upper(),
        "TEN_GA": st_name,
        "MA_GA": st_id,
        "MA_GA_SHORT": st_id,
        "LY_TRINH": "Km1+000 (Auto)", 
        "KET_QUA_LOI_DI": ai_result,
        "ANH_TONG_QUAT": get_img("tong_quat.jpg", 150),
        "ANH_LOI_VAO_1": get_img("loi_vao_1.jpg", 50),
        "ANH_LOI_VAO_2": get_img("loi_vao_2.jpg", 50),
        "ANH_BAI_DO": get_img("bai_xe.jpg", 50),
        "ANH_XE_BUYT": get_img("tram_bus.jpg", 50),
        "ANH_XUNG_DOT": get_img("xung_dot.jpg", 50),
        # Dummy fill for missing things
        "BANDO_1000M": "",
        "ANH_HANH_LANG": "", "ANH_PUDO": "", "MO_TA_TIEN_ICH": "",
        "BE_RONG_DUONG": "N/A", "BE_RONG_VIA_HE": "N/A", "TINH_TRANG_VIA_HE": "N/A", "DE_XUAT_EN1": ""
    }

    # 4. Lưu Word
    print("[4/5] Đang xuất file Word...")
    word_out = os.path.join("output", f"BaoCao_Final_{st_id}.docx")
    tpl.render(context)
    tpl.save(word_out)

    # 4.5. Nhồi toàn bộ ảnh còn dư vào cuối file Word
    if len(all_files) > 0:
        print(f"[*] Phát hiện còn {len(all_files)} ảnh chưa được dán, đang nhồi thêm vào cuối file...")
        doc = docx.Document(word_out)
        doc.add_heading('PHỤ LỤC: CÁC ẢNH KHẢO SÁT KHÁC', level=1)
        for leftover_img in all_files:
            img_path = os.path.join(data_dir, leftover_img)
            try:
                doc.add_picture(img_path, width=docx.shared.Mm(120))
                doc.add_paragraph(f"Tên file: {leftover_img}")
            except Exception as e:
                print(f"Lỗi khi chèn {leftover_img}: {e}")
        doc.save(word_out)

    # 5. Lắp ráp PPTX
    print("[5/5] Đang xử lý file PPTX...")
    try:
        prs = Presentation("C1_Thai Binh Market Station_Maps and Figures.pptx")
        # Đổi title ở slide 1
        if len(prs.slides) > 0 and prs.slides[0].shapes.title:
            prs.slides[0].shapes.title.text = f"{st_id} - {st_name}"
        
        # Dán ảnh tổng quát vào Slide 7 (index 6). Nếu không có tong_quat.jpg thì lấy đại ảnh đầu tiên trong thư mục.
        if len(prs.slides) > 6:
            map_slide = prs.slides[6]
            tong_quat = os.path.join(data_dir, "tong_quat.jpg")
            img_to_add = tong_quat if os.path.exists(tong_quat) else None
            if not img_to_add:
                fallback_imgs = [f for f in os.listdir(data_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if fallback_imgs:
                    img_to_add = os.path.join(data_dir, fallback_imgs[0])
            
            if img_to_add:
                map_slide.shapes.add_picture(img_to_add, Inches(1), Inches(1.5), width=Inches(8))
        
        pptx_out = os.path.join("output", f"Slide_Final_{st_id}.pptx")
        prs.save(pptx_out)
        print(f"XONG! Đã lưu: {word_out} và {pptx_out}")
    except Exception as e:
        print(f"[5/5] Lỗi xuất PPTX: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_agent(sys.argv[1])
    else:
        print("Vui lòng nhập mã ga. VD: python run_agent.py S1")
