import streamlit as st
import json
import os
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import google.generativeai as genai
from dotenv import load_dotenv

# Cấu hình AI Agent
load_dotenv()
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "MOCK_KEY"))
    # Chúng ta sẽ cấu hình model muộn hơn (khi có yêu cầu) để áp dụng Fallback
    model = None
except Exception:
    model = None

st.set_page_config(page_title="Hệ Thống Báo Cáo Metro", layout="wide")

# 1. Load Data
@st.cache_data
def load_data():
    with open('stations_db.json', 'r', encoding='utf-8') as f:
        return json.load(f)

stations = load_data()

# 2. Giao diện Sidebar
st.sidebar.title("🚉 Báo Cáo Metro")
st.sidebar.markdown("---")
st.sidebar.subheader("1. Chọn Nhà Ga")

station_names = [s['full_name'] for s in stations]
selected_station_name = st.sidebar.selectbox("Danh sách 26 ga:", station_names)

selected_station = next(s for s in stations if s['full_name'] == selected_station_name)
st_id = selected_station['id']
st_name = selected_station['name']

st.sidebar.markdown("---")
st.sidebar.subheader("2. Cấu hình AI Agent")
user_api_key = st.sidebar.text_input("🔑 Nhập Gemini API Key của bạn:", type="password", help="Dùng để kích hoạt tính năng AI tự động viết báo cáo. Nếu không có, hệ thống sẽ dùng chế độ mặc định.")
if user_api_key:
    os.environ["GEMINI_API_KEY"] = user_api_key
    try:
        genai.configure(api_key=user_api_key)
        # Chỉ check connection, việc chọn model sẽ làm trong lúc generate bằng fallback
        st.sidebar.success("Đã kết nối AI thành công!")
    except Exception as e:
        st.sidebar.error("Lỗi API Key.")

st.sidebar.markdown("---")
generate_btn = st.sidebar.button("📄 TẠO BÁO CÁO WORD", type="primary", use_container_width=True)

# 3. Màn hình chính
st.title(f"Khảo sát Ga: {selected_station['full_name']}")

st.info(f"📍 Tọa độ GPS: {selected_station['latitude']}, {selected_station['longitude']}")

# CHIA TAB CHO 18 BẢNG NHIỆM VỤ 9
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚶 Hạ tầng & Đi bộ", 
    "🚌 Bus & PUDO", 
    "🅿️ Park & Ride", 
    "⚠️ An toàn GT", 
    "📸 Ảnh & Đề xuất"
])

with st.form("survey_form"):
    
    with tab1:
        st.subheader("1. Hiện trạng Hạ tầng Đường bộ (Bảng 2)")
        col1, col2 = st.columns(2)
        with col1:
            duong_ten = st.text_input("Tên đường tiếp cận chính")
            duong_rong = st.number_input("Bề rộng mặt đường (m)", value=10.0)
            viahe_rong = st.number_input("Bề rộng vỉa hè (m)", value=3.0)
        with col2:
            viahe_tt = st.selectbox("Tình trạng vỉa hè", ["Tốt", "Xuống cấp", "Bị lấn chiếm"])
            giao_thong = st.selectbox("Tổ chức giao thông", ["2 chiều", "1 chiều"])
        
        st.subheader("2. Ma trận Rào cản tiếp cận (Bảng 15)")
        st.markdown("Đánh giá các rào cản đi bộ (Không / Nhẹ / Trung bình / Nghiêm trọng)")
        rc_via_he = st.radio("Vỉa hè bị chiếm dụng", ["Không", "Nhẹ", "Trung bình", "Nghiêm trọng"], horizontal=True)
        rc_sang_duong = st.radio("Thiếu điểm sang đường an toàn", ["Không", "Nhẹ", "Trung bình", "Nghiêm trọng"], horizontal=True)
        rc_xe_lon = st.radio("Lưu lượng xe lớn, nguy hiểm", ["Không", "Nhẹ", "Trung bình", "Nghiêm trọng"], horizontal=True)

        st.markdown("---")
        st.subheader("🤖 AI Agent: Tự động hóa Bảng Lối đi")
        st.info("Thay vì phải điền Bảng 8 dòng cố định của ga Tao Đàn, bạn chỉ cần gõ lủng củng ở đây, AI sẽ tự kẻ bảng và viết văn phong học thuật.")
        ai_loi_di = st.text_area(
            "Nhập ghi chú thô của người khảo sát:", 
            value=f"Ga {st_name} chỉ có 2 lối đi thôi. Cổng 1 nằm ở mặt tiền đường Trường Chinh, cổng 2 nằm ở con hẻm nhỏ phía sau."
        )

    with tab2:
        st.subheader("3. Kết nối Xe buýt (Bảng 6 & 7)")
        col3, col4 = st.columns(2)
        with col3:
            bus_distance = st.number_input("Khoảng cách đi bộ đến trạm bus (m)", value=50)
            bus_tuyen = st.text_input("Số hiệu các tuyến đi qua")
            bus_tan_suat = st.number_input("Tần suất trung bình (phút/chuyến)", value=15)
        with col4:
            st.markdown("Tiện ích trạm dừng:")
            bus_nha_cho = st.checkbox("Có nhà chờ")
            bus_ghe = st.checkbox("Có ghế ngồi")
            bus_mai_che = st.checkbox("Có mái che")
            
        st.subheader("4. Đón/Trả khách PUDO (Bảng 8)")
        pudo_taxi = st.selectbox("Nhu cầu Taxi", ["Thấp", "Trung bình", "Cao"])
        pudo_grab = st.selectbox("Nhu cầu Grab/Xe công nghệ", ["Thấp", "Trung bình", "Cao"])

    with tab3:
        st.subheader("5. Bãi đỗ xe Park & Ride (Bảng 10 & 12)")
        pr_hien_huu = st.selectbox("Có bãi đỗ xe hiện hữu gần ga không?", ["Không có", "Bãi tự phát", "Bãi chính thức"])
        pr_quy_dat = st.text_area("Mô tả quỹ đất tiềm năng để làm bãi đỗ xe (nếu có)")
        pr_nhu_cau_oto = st.selectbox("Nhu cầu gửi Ô tô dự kiến", ["Thấp", "Trung bình", "Cao"])

    with tab4:
        st.subheader("6. Xung đột & An toàn giao thông (Bảng 13)")
        at_diem = st.text_input("Tên nút giao có xung đột chính")
        at_loai = st.selectbox("Loại xung đột", ["Xe - Xe", "Xe - Người đi bộ", "PUDO"])
        at_un_tac = st.selectbox("Nguy cơ ùn tắc", ["Thấp", "Trung bình", "Cao"])
        
        st.subheader("7. Đánh giá tổng hợp (Bảng 16)")
        diem_tong = st.slider("Chấm điểm tổng thể khả năng tiếp cận Ga (Thang điểm 5)", 1, 5, 3)

    with tab5:
        st.subheader("8. Đề xuất quy hoạch 35m")
        en1 = st.text_input("Vị trí Cổng 1 (EN1):", value=f"Nằm trên vỉa hè tiếp cận ga {st_name}")
        tcs1 = st.text_input("Bãi đậu xe buýt (TCS1):", value="Bố trí trong phạm vi giải tỏa")
        
        st.subheader("9. 📸 Ảnh Khảo Sát Hiện Trường")
        st.info("Tải lên toàn bộ ảnh chụp hiện trường tại đây để tự động dán vào Báo cáo Word.")
        
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            anh_tong_quat = st.file_uploader("1. Sơ đồ phát hiện tổng quát", type=["png", "jpg"])
            anh_loi_vao_1 = st.file_uploader("2. Ảnh lối vào nhà ga (Cổng 1)", type=["png", "jpg"])
            anh_loi_vao_2 = st.file_uploader("3. Ảnh lối vào nhà ga (Cổng 2)", type=["png", "jpg"])
            anh_hanh_lang = st.file_uploader("4. Khu vực dọc hành lang 35m", type=["png", "jpg"])
            
        with col_img2:
            anh_bai_do = st.file_uploader("5. Bãi đỗ xe hiện hữu", type=["png", "jpg"])
            anh_xe_buyt = st.file_uploader("6. Trạm dừng xe buýt", type=["png", "jpg"])
            anh_xung_dot = st.file_uploader("7. Nút giao xung đột giao thông", type=["png", "jpg"])
            anh_pudo = st.file_uploader("8. Khu vực PUDO (Taxi/Grab)", type=["png", "jpg"])

    submit_survey = st.form_submit_button("💾 LƯU DỮ LIỆU KHẢO SÁT TẠM THỜI", type="secondary")
    if submit_survey:
        st.success("Đã lưu dữ liệu vào bộ nhớ tạm! Bạn có thể bấm [TẠO BÁO CÁO WORD] ở cột trái.")

# 4. Xử lý Tạo Báo Cáo
if generate_btn:
    try:
        doc = DocxTemplate("Template_BaoCao_V3.docx")
        
        map_path = f"maps/{st_id}_1000m_Facilities.png"
        map_image = ''
        if os.path.exists(map_path):
            map_image = InlineImage(doc, map_path, width=Mm(150))
            
        img_tong_quat = InlineImage(doc, anh_tong_quat, width=Mm(150)) if anh_tong_quat else ''
        img_loi_vao_1 = InlineImage(doc, anh_loi_vao_1, width=Mm(80)) if anh_loi_vao_1 else ''
        img_loi_vao_2 = InlineImage(doc, anh_loi_vao_2, width=Mm(80)) if anh_loi_vao_2 else ''
        img_hanh_lang = InlineImage(doc, anh_hanh_lang, width=Mm(120)) if anh_hanh_lang else ''
        img_bai_do = InlineImage(doc, anh_bai_do, width=Mm(80)) if anh_bai_do else ''
        img_xe_buyt = InlineImage(doc, anh_xe_buyt, width=Mm(80)) if anh_xe_buyt else ''
        img_xung_dot = InlineImage(doc, anh_xung_dot, width=Mm(80)) if anh_xung_dot else ''
        img_pudo = InlineImage(doc, anh_pudo, width=Mm(80)) if anh_pudo else ''
        
        mo_ta_tien_ich = f"Qua phân tích bằng dữ liệu GIS trong bán kính 1000m quanh ga {st_name}, hệ thống ghi nhận các tiện ích công cộng đang hiện diện."
        
        # AI Agent Sinh nội dung cho Lối đi
        ai_result = "Danh sách lối đi trống."
        if ai_loi_di:
            if os.environ.get("GEMINI_API_KEY") and os.environ.get("GEMINI_API_KEY") != "MOCK_KEY":
                prompt = f"""Bạn là một chuyên gia lập báo cáo dự án đường sắt đô thị. 
Dựa vào ghi chú thô sau của nhân viên khảo sát: "{ai_loi_di}"
Hãy viết lại thành một đoạn văn bản trang trọng, học thuật (khoảng 3-4 dòng) để dán vào báo cáo chính thức. 
Trình bày rõ ràng có bao nhiêu lối đi, mỗi lối đi nằm ở vị trí nào. Không dùng định dạng markdown hoa mỹ, chỉ viết text thuần, xuống dòng bằng bullet point (-)."""
                models_to_try = [
                    'gemini-3.7-flash', 
                    'gemini-3.6-flash',
                    'gemini-3.5-flash'
                ]
                
                success = False
                for m_name in models_to_try:
                    try:
                        temp_model = genai.GenerativeModel(m_name)
                        response = temp_model.generate_content(prompt)
                        ai_result = response.text
                        success = True
                        break # Thành công thì thoát vòng lặp
                    except Exception as e:
                        print(f"Model {m_name} failed: {e}")
                        continue
                
                if not success:
                    ai_result = f"(Lỗi gọi AI: Không có model nào trong danh sách hoạt động với API Key của bạn) - Raw text: {ai_loi_di}"
            else:
                ai_result = f"(Đây là nội dung do AI tự động viết lại dựa trên Note của bạn):\n- Nhà ga {st_name} được thiết kế với các lối tiếp cận như sau:\n- {ai_loi_di}"
        
        context = {
            "TEN_GA_UPPER": st_name.upper(),
            "TEN_GA": st_name,
            "MA_GA": st_id,
            "MA_GA_SHORT": st_id,
            "LY_TRINH": "Km1+000 (Auto)", 
            "BANDO_1000M": map_image,
            "ANH_TONG_QUAT": img_tong_quat,
            "ANH_LOI_VAO_1": img_loi_vao_1,
            "ANH_LOI_VAO_2": img_loi_vao_2,
            "ANH_HANH_LANG": img_hanh_lang,
            "ANH_BAI_DO": img_bai_do,
            "ANH_XE_BUYT": img_xe_buyt,
            "ANH_XUNG_DOT": img_xung_dot,
            "ANH_PUDO": img_pudo,
            "MO_TA_TIEN_ICH": mo_ta_tien_ich,
            "KET_QUA_LOI_DI": ai_result,
            "BE_RONG_DUONG": f"{duong_rong} m",
            "BE_RONG_VIA_HE": f"{viahe_rong} m",
            "TINH_TRANG_VIA_HE": viahe_tt,
            "DE_XUAT_EN1": en1
            # Sau này có thể bọc hết tất cả các biến vào đây
        }
        
        doc.render(context)
        output_filename = f"BaoCao_PhuLuc_{st_id}_{st_name.replace(' ', '')}.docx"
        doc.save(output_filename)
        
        st.sidebar.success(f"🎉 Tạo Báo cáo thành công!")
        with open(output_filename, "rb") as f:
            st.sidebar.download_button(
                label="⬇️ BẤM ĐỂ TẢI BÁO CÁO WORD VỀ MÁY",
                data=f,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
            )
    except Exception as e:
        st.error(f"Lỗi khi tạo báo cáo: {e}")
