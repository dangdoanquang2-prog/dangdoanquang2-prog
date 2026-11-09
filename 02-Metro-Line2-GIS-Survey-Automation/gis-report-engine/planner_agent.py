import sys
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_station_info(st_id):
    try:
        with open("stations_db.json", "r", encoding="utf-8") as f:
            db = json.load(f)
            for st in db:
                if st.get("id") == st_id:
                    # Chữa lỗi font Unicode bị hỏng trong file json
                    return st.get("full_name").split(" - ")[-1]
            return "Unknown Station"
    except:
        return "Unknown Station"

def generate_survey_plan(st_id, st_name):
    # Đây chính là MASTER PROMPT dành cho Agent Đội trưởng
    prompt = f"""Bạn là Đội Trưởng Quản lý Khảo sát Dự án Đường sắt Đô thị (Metro). 
Nhiệm vụ của bạn là LẬP KẾ HOẠCH KHẢO SÁT THỰC ĐỊA chi tiết cho nhân viên cấp dưới.

Nhà ga mục tiêu hôm nay: {st_id} - {st_name}

Dựa vào kiến thức địa lý của bạn về khu vực ga này (hoặc suy luận logic về quy hoạch đô thị), hãy lập một bản Hướng dẫn Khảo sát (Action Plan) thật ngắn gọn, gạch đầu dòng rõ ràng để nhân viên đọc trên điện thoại trước khi đi.

Bản hướng dẫn phải gồm các mục:
1. NHIỆM VỤ CHÍNH: (Mục tiêu khảo sát ga này là gì)
2. CÁC TUYẾN ĐƯỜNG CẦN QUÉT: (Liệt kê 2-3 con đường giao cắt xung quanh ga {st_name} cần đi bộ để đo vỉa hè)
3. TRẠM XE BUÝT CẦN TÌM: (Cần tìm trạm xe buýt trên đường nào gần đó)
4. BÃI ĐỖ XE & ĐIỂM ĐÓN TRẢ (PUDO): (Gợi ý nhân viên chú ý các khu vực nào dễ làm bãi đỗ xe)
5. CẢNH BÁO THỰC ĐỊA: (Khu vực này thường kẹt xe giờ nào, vướng mắc gì cần cẩn thận chụp ảnh lại)

Lưu ý: Viết ngôn từ chuyên nghiệp, dứt khoát như một người sếp giao việc. Không viết dài dòng.
"""

    print(f"[*] Đang triệu hồi AI Đội Trưởng lên kế hoạch cho Ga {st_name}...")
    
    models_to_try = ['gemini-3.7-flash', 'gemini-3.6-flash', 'gemini-3.5-flash']
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
    
    for m_name in models_to_try:
        try:
            model = genai.GenerativeModel(m_name)
            resp = model.generate_content(prompt)
            return resp.text
        except Exception as e:
            continue
            
    return "Lỗi: Không thể kết nối với AI Đội Trưởng."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        st_id = sys.argv[1]
        st_name = get_station_info(st_id)
        
        plan = generate_survey_plan(st_id, st_name)
        
        out_dir = os.path.join("data", st_id)
        os.makedirs(out_dir, exist_ok=True)
        
        out_file = os.path.join(out_dir, "KE_HOACH_KHAO_SAT.txt")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(plan)
            
        print("\n" + "="*50)
        print(plan)
        print("="*50)
        print(f"\n[Thành công] Đã lưu Kế hoạch khảo sát vào: {out_file}")
        print("Nhân viên chỉ cần mở file này đọc trước khi ra công trường!")
    else:
        print("Vui lòng nhập mã ga. VD: python planner_agent.py S1")
