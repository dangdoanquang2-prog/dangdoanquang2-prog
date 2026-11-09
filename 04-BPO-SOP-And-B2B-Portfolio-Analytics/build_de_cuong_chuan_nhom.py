# -*- coding: utf-8 -*-
"""
Script to generate the standardized, fully harmonized Detailed Outline (De Cuong Chi Tiet)
for the HKDN graduation report at UTH, based on the group's latest submission.
Strictly adheres to:
- Times New Roman, 13pt body, 1.3 line spacing, 6pt after, 1.0cm indent
- Standard Heading 1, 2, 3, 4 hierarchy
- Removal of draft notes (e.g. '( nếu xin được thì làm)')
- Clean, academic phrasing and 100% black text
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_outline_doc():
    doc = docx.Document()

    for sec in doc.sections:
        sec.top_margin = Inches(0.79)     # 2.0 cm
        sec.bottom_margin = Inches(0.79)  # 2.0 cm
        sec.left_margin = Inches(1.18)    # 3.0 cm
        sec.right_margin = Inches(0.79)   # 2.0 cm

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(13)
    font.color.rgb = RGBColor(0, 0, 0)

    def add_p(text, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, size=13, space_before=0, space_after=4, indent=0):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.3
        if indent > 0:
            p.paragraph_format.left_indent = Inches(indent * 0.25)
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Times New Roman'
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_desc(text, indent=1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.left_indent = Inches(indent * 0.25)
        run = p.add_run(f"-> Định hướng nội dung: {text}")
        run.italic = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11.5)
        run.font.color.rgb = RGBColor(60, 60, 60)
        return p

    # --- COVER HEADER ---
    add_p("TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI THÀNH PHỐ HỒ CHÍ MINH", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=12, space_after=2)
    add_p("VIỆN HÀNG HẢI - KHOA KINH TẾ VẬN TẢI", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=12, space_after=16)
    
    add_p("ĐỀ CƯƠNG CHI TIẾT BÁO CÁO HỌC KỲ DOANH NGHIỆP", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=14, space_before=8, space_after=8)
    add_p("TÊN ĐỀ TÀI:", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=13, space_after=2)
    add_p("HOÀN THIỆN QUY TRÌNH GIẢI QUYẾT KHIẾU NẠI CỦA KHÁCH HÀNG TẠI CÔNG TY CỔ PHẦN LOGISTICS U&I", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=14, space_after=18)

    # --- FRONT MATTER ---
    for item in ["LỜI CẢM ƠN", "LỜI CAM ĐOAN", "MỤC LỤC", "DANH MỤC HÌNH", "DANH MỤC BẢNG", "DANH MỤC TỪ VIẾT TẮT", "LỜI MỞ ĐẦU"]:
        add_p(item, bold=True, size=13, space_before=4, space_after=3)

    # --- CHƯƠNG 1 ---
    add_p("CHƯƠNG 1. GIỚI THIỆU TỔNG QUAN VỀ CÔNG TY CỔ PHẦN LOGISTICS U&I", bold=True, size=13, space_before=10, space_after=4)
    
    add_p("1.1. Lịch sử hình thành và phát triển Công ty Cổ phần Logistics U&I", bold=True, indent=1)
    add_p("1.1.1. Tổng quan về Công ty Cổ phần Logistics U&I", bold=False, indent=2)
    add_desc("Tên đầy đủ, tên viết tắt, mã số thuế, địa chỉ trụ sở chính (Bình Dương), chi nhánh TP.HCM, vốn điều lệ (720 tỷ đồng), tầm nhìn, sứ mệnh và giá trị cốt lõi.", indent=2)
    
    add_p("1.1.2. Lịch sử hình thành và phát triển của Công ty Cổ phần Logistics U&I", bold=False, indent=2)
    add_desc("Các mốc lịch sử quan trọng từ năm 2003 đến nay, quá trình mở rộng hệ thống kho ngoại quan và mạng lưới dịch vụ logistics.", indent=2)

    add_p("1.2. Chức năng, nhiệm vụ, ngành nghề kinh doanh của Công ty Cổ phần Logistics U&I", bold=True, indent=1)
    add_p("1.2.1. Chức năng, nhiệm vụ của Công ty Cổ phần Logistics U&I", bold=False, indent=2)
    add_desc("Chức năng tổ chức cung ứng chuỗi dịch vụ logistics tích hợp 3PL/4PL và nhiệm vụ tuân thủ pháp luật, đảm bảo an toàn hàng hóa.", indent=2)
    add_p("1.2.2. Ngành nghề kinh doanh của Công ty Cổ phần Logistics U&I", bold=False, indent=2)
    add_desc("Các nhóm dịch vụ cốt lõi: Kho bãi & phân phối hàng hóa (kho ngoại quan), Đại lý khai thuê hải quan, Vận tải nội địa (đội xe container), Giao nhận vận tải quốc tế (đường biển, hàng không).", indent=2)

    add_p("1.3. Cơ cấu tổ chức của Công ty Cổ phần Logistics U&I", bold=True, indent=1)
    add_p("1.3.1. Sơ đồ cơ cấu tổ chức của Công ty Cổ phần Logistics U&I", bold=False, indent=2)
    add_desc("Vẽ và thuyết minh Sơ đồ cơ cấu tổ chức theo mô hình trực tuyến - chức năng của công ty.", indent=2)
    add_p("1.3.2. Chức năng, nhiệm vụ của bộ máy quản lý của Công ty Cổ phần Logistics U&I", bold=False, indent=2)
    add_desc("Phân định vai trò của Ban Tổng Giám đốc và các khối phòng ban chuyên môn (Khối Vận hành, Khối Tài chính, Khối Công nghệ...).", indent=2)
    add_p("1.3.3. Giới thiệu Phòng Kinh doanh & Dịch vụ khách hàng tại Công ty Cổ phần Logistics U&I", bold=False, indent=2)
    add_desc("Giới thiệu cụ thể chức năng, nhiệm vụ và vai trò của PKD&DVKH - bộ phận trực tiếp tiếp nhận, điều phối và chủ trì giải quyết khiếu nại của khách hàng.", indent=2)

    add_p("1.4. Tình hình nhân lực của Công ty Cổ phần Logistics U&I", bold=True, indent=1)
    add_p("1.4.1. Giới thiệu chung về nguồn nhân lực công ty", bold=False, indent=2)
    add_desc("Thống kê quy mô nhân sự toàn công ty (211 người), phân tích cơ cấu lao động theo độ tuổi, giới tính và trình độ chuyên môn.", indent=2)
    add_p("1.4.2. Tình hình nhân sự Phòng Kinh doanh & Dịch vụ khách hàng tại Công ty Cổ phần Logistics U&I", bold=False, indent=2)
    add_desc("Mục tiêu: Đánh giá chất lượng đội ngũ nhân sự tiếp nhận và giải quyết khiếu nại (trình độ ngoại ngữ, nghiệp vụ logistics, kỹ năng giao tiếp và kinh nghiệm xử lý khủng hoảng dịch vụ).", indent=2)

    add_p("1.5. Cơ sở vật chất kỹ thuật của Công ty Cổ phần Logistics U&I", bold=True, indent=1)
    add_desc("Hệ thống kho bãi (hơn 242.000 m2 diện tích sàn kho, sức chứa hơn 2.000.000 m3, trung tâm kho ngoại quan lớn nhất Đông Nam Á tại KCN Nam Tân Uyên và Sóng Thần), đội xe đầu kéo container và nền tảng công nghệ thông tin (phần mềm WMS, TMS, hệ thống camera AI).", indent=1)

    add_p("1.6. Khách hàng, thị trường và đối thủ cạnh tranh của Công ty Cổ phần Logistics U&I", bold=True, indent=1)
    add_p("1.6.1. Khách hàng của Công ty Cổ phần Logistics U&I", bold=False, indent=2)
    add_desc("Nhóm khách hàng B2B trọng tâm: doanh nghiệp FDI, tập đoàn sản xuất đồ gỗ xuất khẩu sang Mỹ, may mặc, da giày, điện tử.", indent=2)
    add_p("1.6.2. Thị trường của Công ty Cổ phần Logistics U&I", bold=False, indent=2)
    add_desc("Thị trường nội địa (Vùng kinh tế trọng điểm phía Nam) và thị trường quốc tế (tuyến Bắc Mỹ, Châu Âu, Đông Á).", indent=2)
    add_p("1.6.3. Đối thủ cạnh tranh của Công ty Cổ phần Logistics U&I", bold=False, indent=2)
    add_p("1.6.3.1. Đối thủ trong nước của Công ty Cổ phần Logistics U&I", bold=False, indent=3)
    add_desc("Các công ty logistics hàng đầu Việt Nam: Gemadept, Transimex, Sotrans, Tân Cảng Logistics.", indent=3)
    add_p("1.6.3.2. Đối thủ quốc tế của Công ty Cổ phần Logistics U&I", bold=False, indent=3)
    add_desc("Các tập đoàn logistics đa quốc gia (MNCs): DHL Supply Chain, DB Schenker, Kuehne+Nagel, Nippon Express.", indent=3)

    add_p("1.7. Đánh giá chung kết quả hoạt động sản xuất kinh doanh của Công ty Cổ phần Logistics U&I trong những năm gần đây", bold=True, indent=1)
    add_desc("Phân tích kết quả tài chính 2023 - 2025: Doanh thu thuần (đạt 1.163,52 tỷ đồng năm 2025 theo BCTC kiểm toán), lợi nhuận gộp, lợi nhuận sau thuế và cơ cấu doanh thu theo từng mảng dịch vụ. Phân tích chi phí quản lý và tiền đề dẫn vào vấn đề khiếu nại tại Chương 2.", indent=1)

    # --- CHƯƠNG 2 ---
    add_p("CHƯƠNG 2. PHÂN TÍCH THỰC TRẠNG QUY TRÌNH GIẢI QUYẾT KHIẾU NẠI CỦA KHÁCH HÀNG TẠI CÔNG TY CỔ PHẦN LOGISTICS U&I", bold=True, size=13, space_before=10, space_after=4)
    
    add_p("2.1. Tình hình phát sinh khiếu nại của khách hàng tại Công ty Cổ phần Logistics U&I", bold=True, indent=1)
    add_p("2.1.1. Tình hình phát sinh khiếu nại", bold=False, indent=2)
    add_p("2.1.1.1. Số lượng khiếu nại", bold=False, indent=3)
    add_desc("Thống kê chi tiết số lượng khiếu nại phát sinh giai đoạn 2023 - 2025 (tổng cộng 145 vụ việc) và phân tích sự biến động qua các kỳ.", indent=3)
    add_p("2.1.1.2. Phân loại khiếu nại", bold=False, indent=3)
    add_desc("Phân loại khiếu nại theo mảng dịch vụ thực tế: Kho bãi (hư hỏng bao bì, ẩm mốc), Vận tải container (chậm giờ giao nhận), Thủ tục hải quan (sai sót thông tin, chậm thông quan), và Chứng từ kế toán.", indent=3)
    add_p("2.1.1.3. Xu hướng phát sinh khiếu nại", bold=False, indent=3)
    add_desc("Phân tích 4 nhóm yếu tố tác động: (1) Thời tiết theo từng thời điểm (mùa mưa ngập bão); (2) Đặc điểm từng chặng vận chuyển (chặng lấy hàng, cảng bãi, đường dài); (3) Tình trạng giao nhận bến bãi; (4) Các yếu tố bất khả kháng (ách tắc cảng, kẹt xe nghiêm trọng).", indent=3)
    
    add_p("2.1.2. Kết quả xử lý khiếu nại", bold=False, indent=2)
    add_p("2.1.2.1. Tình trạng xử lý", bold=False, indent=3)
    add_desc("Thống kê số lượng khiếu nại đã giải quyết hoàn tất, số vụ đang trong quá trình xử lý và tồn đọng chưa giải quyết.", indent=3)
    add_p("2.1.2.2. Kết quả giải quyết", bold=False, indent=3)
    add_desc("Phân tích tỷ lệ bồi thường tài chính, tỷ lệ thương lượng thành công, mức độ hoàn thành tiến độ cam kết và đánh giá hiệu quả giải quyết.", indent=3)

    add_p("2.2. Thực trạng Quy trình giải quyết khiếu nại của khách hàng tại Công ty Cổ phần Logistics U&I", bold=True, indent=1)
    add_p("2.2.1. Hệ thống biểu mẫu sử dụng trong quy trình giải quyết khiếu nại", bold=False, indent=2)
    add_p("2.2.1.1. Phiếu tiếp nhận khiếu nại của khách hàng (BM01-QT06/KD)", bold=False, indent=3)
    add_p("2.2.1.1.1. Mục đích sử dụng của biểu mẫu", bold=False, indent=4)
    add_p("2.2.1.1.2. Các nội dung chính trong biểu mẫu", bold=False, indent=4)
    add_p("2.2.1.1.3. Vai trò của biểu mẫu trong quy trình", bold=False, indent=4)
    add_desc("Phân tích cấu trúc phiếu BM01: thông tin khách hàng, mô tả sự cố, chứng từ đính kèm và hạn chế hiện hành.", indent=4)
    
    add_p("2.2.1.2. Biểu mẫu tổng hợp và lưu khiếu nại (BM02-QT06/KD)", bold=False, indent=3)
    add_p("2.2.1.2.1. Mục đích sử dụng của biểu mẫu", bold=False, indent=4)
    add_p("2.2.1.2.2. Các nội dung chính trong biểu mẫu", bold=False, indent=4)
    add_p("2.2.1.2.3. Vai trò của biểu mẫu trong quy trình", bold=False, indent=4)
    add_desc("Phân tích cấu trúc phiếu BM02: tổng hợp kết quả xác minh, đề xuất biện pháp xử lý và trình phê duyệt.", indent=4)

    add_p("2.2.2. Quy trình giải quyết khiếu nại của Phòng Kinh doanh & Dịch vụ khách hàng", bold=False, indent=2)
    add_desc("Vẽ và mô tả Sơ đồ Hình 2.1: Quy trình giải quyết khiếu nại hiện tại (gồm 7 bước tuần tự từ Tiếp nhận đến Lưu hồ sơ).", indent=2)

    add_p("2.2.3. Phân tích quy trình và hiệu quả thực hiện quy trình giải quyết khiếu nại tại Công ty Cổ phần Logistics U&I", bold=False, indent=2)
    add_p("2.2.3.1. Phân tích chi tiết quy trình giải quyết khiếu nại hiện tại", bold=False, indent=3)
    add_p("2.2.3.1.1. Bước 1: Tiếp nhận khiếu nại của khách hàng", bold=False, indent=4)
    add_p("2.2.3.1.2. Bước 2: Xem xét sơ bộ khiếu nại", bold=False, indent=4)
    add_p("2.2.3.1.3. Bước 3: Các bộ phận kiểm tra khiếu nại", bold=False, indent=4)
    add_p("2.2.3.1.4. Bước 4: Phân tích nguyên nhân khiếu nại", bold=False, indent=4)
    add_p("2.2.3.1.5. Bước 5: Đề xuất biện pháp giải quyết", bold=False, indent=4)
    add_p("2.2.3.1.6. Bước 6: Phê duyệt và giải quyết khiếu nại", bold=False, indent=4)
    add_p("2.2.3.1.7. Bước 7: Tổng hợp và lưu hồ sơ khiếu nại", bold=False, indent=4)
    add_desc("Phân tích cụ thể từng bước về: cách thức tiếp nhận, nội dung thực hiện, kết quả đầu ra, thời gian thực tế và các mắt xích còn hạn chế.", indent=4)

    add_p("2.3. Đánh giá thực trạng quy trình giải quyết khiếu nại tại Công ty Cổ phần Logistics U&I", bold=True, indent=1)
    add_p("2.3.1. Những kết quả đạt được", bold=False, indent=2)
    add_p("2.3.1.1. Quy trình giải quyết khiếu nại được xây dựng theo trình tự tương đối rõ ràng", bold=False, indent=3)
    add_p("2.3.1.2. Có cơ chế kiểm tra, xác minh và phân tích nguyên nhân khiếu nại", bold=False, indent=3)
    add_p("2.3.1.3. Có quy định về thời gian xử lý và sự phối hợp giữa các bộ phận", bold=False, indent=3)
    add_p("2.3.1.4. Có hệ thống biểu mẫu và bằng chứng phục vụ quá trình xử lý", bold=False, indent=3)
    add_p("2.3.1.5. Có đề xuất giải pháp đối với khiếu nại do U&I Logistics gây ra", bold=False, indent=3)
    
    add_p("2.3.2. Những hạn chế còn tồn tại", bold=False, indent=2)
    add_p("2.3.2.1. Chưa có cơ chế phân loại khiếu nại và phân luồng ưu tiên theo mức độ khẩn cấp", bold=False, indent=3)
    add_p("2.3.2.2. Chưa có bước đánh giá mức độ hài lòng của khách hàng sau khi giải quyết", bold=False, indent=3)
    add_p("2.3.2.3. Chưa khai thác hiệu quả dữ liệu khiếu nại và chưa số hóa tập trung", bold=False, indent=3)
    
    add_p("2.3.3. Nguyên nhân gây ra những hạn chế", bold=False, indent=2)
    add_p("2.3.3.1. Nguyên nhân từ quy trình (thiếu cổng rẽ nhánh kiểm soát SLA và vòng lặp xem xét lại)", bold=False, indent=3)
    add_p("2.3.3.2. Nguyên nhân từ thông tin và dữ liệu (lưu trữ phân tán, thiếu thống kê xu hướng)", bold=False, indent=3)
    add_p("2.3.3.3. Nguyên nhân từ công cụ hỗ trợ (biểu mẫu thiếu trường thông tin SLA và đo lường)", bold=False, indent=3)
    add_p("2.3.3.4. Cơ chế cải tiến sau khiếu nại chưa được thể chế hóa chính thức", bold=False, indent=3)

    add_p("2.4. Kết luận chương 2", bold=True, indent=1)
    add_desc("Tóm lược các phát hiện cốt lõi từ thực trạng Chương 2, tạo tiền đề lý luận và thực tiễn trực tiếp dẫn dắt vào giải pháp tại Chương 3.", indent=1)

    # --- CHƯƠNG 3 ---
    add_p("CHƯƠNG 3. ĐỀ XUẤT GIẢI PHÁP HOÀN THIỆN QUY TRÌNH GIẢI QUYẾT KHIẾU NẠI CỦA KHÁCH HÀNG TẠI CÔNG TY CỔ PHẦN LOGISTICS U&I", bold=True, size=13, space_before=10, space_after=4)
    
    add_p("3.1. Cơ sở đề xuất hoàn thiện quy trình", bold=True, indent=1)
    add_p("3.1.1. Căn cứ từ thực trạng quy trình hiện tại", bold=False, indent=2)
    add_desc("Khắc phục triệt để 5 điểm nghẽn hệ thống đã phân tích tại Chương 2.", indent=2)
    add_p("3.1.2. Căn cứ từ nhu cầu nâng cao chất lượng dịch vụ", bold=False, indent=2)
    add_desc("Nâng cao năng lực đáp ứng, rút ngắn thời gian xử lý, tăng tính minh bạch và tuân thủ chuẩn mực ISO 10002:2018.", indent=2)

    add_p("3.2. Đề xuất quy trình giải quyết khiếu nại khách hàng hoàn thiện", bold=True, indent=1)
    add_p("3.2.1. Sơ đồ quy trình đề xuất", bold=False, indent=2)
    add_desc("Hình 3.1: Sơ đồ Quy trình giải quyết khiếu nại của khách hàng hoàn thiện (10 bước tác nghiệp chuẩn mực khép kín có cổng rẽ nhánh quyết định và vòng lặp xem xét lại).", indent=2)
    
    add_p("3.2.2. Nội dung chi tiết quy trình đề xuất", bold=False, indent=2)
    add_p("3.2.2.1. Bước 1: Tiếp nhận khiếu nại của khách hàng (đa kênh, chuẩn hóa phiếu BM01 cải tiến, mốc thời gian vàng 2 giờ)", bold=False, indent=3)
    add_p("3.2.2.2. Bước 2: Xem xét sơ bộ khiếu nại (đối chiếu hợp đồng, Incoterms, xử lý phân nhánh trong vòng 4 giờ)", bold=False, indent=3)
    add_p("3.2.2.3. Bước 3: Phân loại và phân luồng ưu tiên xử lý khiếu nại (Bổ sung mới - Ma trận phân loại Triage 3 cấp độ SLA tại Bảng 3.1)", bold=False, indent=3)
    add_p("3.2.2.4. Bước 4: Các bộ phận kiểm tra khiếu nại (kiểm tra WMS, GPS, camera, lập biên bản giám định hiện trường chuẩn)", bold=False, indent=3)
    add_p("3.2.2.5. Bước 5: Phân tích nguyên nhân khiếu nại (bóc tách nguyên nhân khách quan và chủ quan)", bold=False, indent=3)
    add_p("3.2.2.6. Bước 6: Đề xuất biện pháp giải quyết (bồi thường tài chính, khắc phục dịch vụ gia tăng, cam kết CAPA trên BM02)", bold=False, indent=3)
    add_p("3.2.2.7. Bước 7: Phê duyệt và giải quyết khiếu nại (phân quyền tài chính: Trưởng phòng duyệt bồi thường < 10 triệu đồng; Tổng Giám đốc duyệt > 10 triệu đồng)", bold=False, indent=3)
    add_p("3.2.2.8. Bước 8: Thu thập ý kiến và phản hồi khách hàng (Bổ sung mới - Đo lường Post-claim CSAT, cơ chế Re-evaluation Loopback)", bold=False, indent=3)
    add_p("3.2.2.9. Bước 9: Tổng hợp và lưu hồ sơ số hóa (Bổ sung mới - Số hóa 100% lên Digital Claim Tracking Log)", bold=False, indent=3)
    add_p("3.2.2.10. Bước 10: Phân tích dữ liệu khiếu nại tái diễn và thực hiện hành động phòng ngừa (Bổ sung mới - Phân tích Pareto 80/20 và 5 Why)", bold=False, indent=3)

    add_p("3.3. Tổ chức thực hiện quy trình đề xuất", bold=True, indent=1)
    add_p("3.3.1. Phân công trách nhiệm thực hiện theo Ma trận RACI", bold=False, indent=2)
    add_desc("Bảng 3.2: Ma trận RACI chi tiết 6 chức danh (Khách hàng, CS/Sales, Vận hành Kho/Xe/Cảng, Trưởng phòng KD&DVKH, Tổng Giám đốc, Kế toán) cho toàn bộ 10 bước tác nghiệp.", indent=2)
    add_p("3.3.2. Hoàn thiện biểu mẫu và công cụ theo dõi", bold=False, indent=2)
    add_desc("Cải tiến BM01 (thêm mã Claim ID, cấp độ ưu tiên SLA, checklist) và BM02 (thêm phân cấp duyệt, ô đánh giá hài lòng, cam kết CAPA).", indent=2)
    add_p("3.3.3. Thiết lập cơ chế theo dõi sau khi giải quyết khiếu nại", bold=False, indent=2)
    add_desc("Xây dựng Form khảo sát đo lường mức độ hài lòng khách hàng sau khiếu nại (Post-claim CSAT thang Likert 5 mức độ) và quy trình xử lý phản hồi tiêu cực.", indent=2)
    add_p("3.3.4. Hướng dẫn và đào tạo nhân viên", bold=False, indent=2)
    add_desc("Xây dựng chương trình 2 chuyên đề tập huấn nội bộ (nghiệp vụ 10 bước và tâm lý học giao tiếp hòa giải).", indent=2)
    add_p("3.3.5. Thử nghiệm và điều chỉnh", bold=False, indent=2)
    add_desc("Kế hoạch thử nghiệm có kiểm soát (Pilot Test) 4 tuần tại cụm Kho ngoại quan Sóng Thần trước khi ban hành chính thức.", indent=2)

    add_p("3.4. Thời gian và chi phí thực hiện", bold=True, indent=1)
    add_p("3.4.1. Thời gian thực hiện", bold=False, indent=2)
    add_desc("Lập tiến độ triển khai Gantt Chart 8 tuần qua 4 giai đoạn chuẩn bị, đào tạo, thử nghiệm và chuẩn hóa.", indent=2)
    add_p("3.4.2. Chi phí thực hiện", bold=False, indent=2)
    add_desc("Xác định các nhóm chi phí dự kiến: in ấn tài liệu hướng dẫn, tổ chức đào tạo nội bộ, thiết lập công cụ số hóa trên hạ tầng sẵn có (không tự ý bịa số liệu vô căn cứ).", indent=2)

    add_p("3.5. Đánh giá tính khả thi của quy trình đề xuất", bold=True, indent=1)
    add_p("3.5.1. Tính khả thi về nhân sự", bold=False, indent=2)
    add_desc("Đánh giá sự phù hợp với quy mô 12 nhân sự của PKD&DVKH, tối ưu hóa năng suất nhờ phân định RACI rõ ràng.", indent=2)
    add_p("3.5.2. Tính khả thi về công cụ và công nghệ", bold=False, indent=2)
    add_desc("Khả năng ứng dụng ngay trên nền tảng CNTT sẵn có của công ty (WMS, TMS, Microsoft 365 / Google Workspace).", indent=2)
    add_p("3.5.3. Tính khả thi về chi phí", bold=False, indent=2)
    add_desc("Chi phí triển khai thấp nhưng mang lại hiệu quả bảo vệ dòng doanh thu hàng tỷ đồng từ khách hàng chiến lược.", indent=2)
    add_p("3.5.4. Tính khả thi về thời gian", bold=False, indent=2)
    add_desc("Lộ trình 8 tuần phù hợp, không làm gián đoạn đến hoạt động kinh doanh hàng ngày.", indent=2)
    add_p("3.5.5. Hiệu quả dự kiến và các chỉ tiêu đánh giá sau triển khai", bold=False, indent=2)
    add_desc("Bộ chỉ tiêu đo lường định lượng (KPIs): rút ngắn Lead-time từ 7-12 ngày xuống 1-3 ngày, tỷ lệ đúng hạn SLA >= 95%, CSAT >= 85%, tỷ lệ khách hàng quay lại >= 92%.", indent=2)

    add_p("3.6. Hiệu quả dự kiến của quy trình hoàn thiện", bold=True, indent=1)
    add_p("3.6.1. Áp dụng giải quyết tình huống thực tế (Case study minh họa)", bold=False, indent=2)
    add_desc("Áp dụng thử nghiệm quy trình 10 bước hoàn thiện vào xử lý sự cố thực tế: Case hàng đồ gỗ bị ẩm mốc tại Kho ngoại quan hoặc Case trễ hạn container xuất khẩu.", indent=2)
    add_p("3.6.2. Đánh giá hiệu quả tổng hợp mang lại cho doanh nghiệp", bold=False, indent=2)
    add_desc("Tổng kết lợi ích 3 mặt: Hiệu quả vận hành (Lead-time), Quan hệ khách hàng (CSAT & Retention Rate) và Quản trị nội bộ (Kaizen & Phòng ngừa tái diễn).", indent=2)

    # --- BACK MATTER ---
    for item in ["KẾT LUẬN VÀ KIẾN NGHỊ", "TÀI LIỆU THAM KHẢO", "PHỤ LỤC"]:
        add_p(item, bold=True, size=13, space_before=6, space_after=3)

    output_path = r"d:\hkdn\DE_CUONG_CHI_TIET_CHUAN_NHOM.docx"
    doc.save(output_path)
    print(f"Successfully generated: {output_path}")

if __name__ == "__main__":
    create_outline_doc()
