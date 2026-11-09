import sys, os, re

script_path = r"d:\hkdn\build_master_khieu_nai_full_complete.py"
with open(script_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update format_source_caption_p
old_source_caption = '''    clean = txt.strip().replace('\\n', ' ')
    if clean == "(Nguồn: Công ty Cổ phần Logistics U&I,[8])":
        clean = "(Nguồn: Công ty Cổ phần Logistics U&I, [8])"'''

new_source_caption = '''    clean = txt.strip().replace('\\n', ' ')
    if "(Nguồn: Công ty Cổ phần Logistics U&I, [1])" in clean or clean == "(Nguồn: Công ty Cổ phần Logistics U&I, [1])":
        clean = "(Nguồn: Công ty Cổ phần Logistics U&I, [15])"
    elif "(Nguồn: Công ty Cổ phần Logistics U&I,[8])" in clean or "(Nguồn: Công ty Cổ phần Logistics U&I, [8])" in clean:
        clean = "(Nguồn: Công ty Cổ phần Logistics U&I, [22])"'''

assert old_source_caption in code, "old_source_caption not found!"
code = code.replace(old_source_caption, new_source_caption, 1)

# 2. Update replace_chapter1_citations and replace_chapter23_citations
old_citation_funcs = '''def replace_chapter1_citations(t):
    """Bảo toàn 100% trích dẫn gốc [1]-[8] của nhóm bạn trong Chương 1"""
    return t

def replace_chapter23_citations(t):
    """Bảo toàn 100% trích dẫn gốc [9], [10], [6], [4], [2], [11] của nhóm bạn trong Chương 2 & 3"""
    return t'''

new_citation_funcs = '''def replace_chapter1_citations(t):
    """Ánh xạ trích dẫn Chương 1: [1]-[8] sang các website [15]-[22]"""
    mapping = {
        r'\\[1\\]': '[15]',
        r'\\[2\\]': '[16]',
        r'\\[3\\]': '[17]',
        r'\\[4\\]': '[18]',
        r'\\[5\\]': '[19]',
        r'\\[6\\]': '[20]',
        r'\\[7\\]': '[21]',
        r'\\[8\\]': '[22]'
    }
    for pattern, repl in mapping.items():
        t = re.sub(pattern, repl, t)
    return t

def replace_chapter23_citations(t):
    """Ánh xạ các số trích dẫn còn lại trong Chương 2 & 3 sang danh mục chuẩn"""
    t = t.replace("[9], [10]", "[23], [24]")
    t = t.replace("[6]", "[20]")
    t = t.replace("[4]", "[18]")
    t = t.replace("[2]", "[16]")
    t = t.replace("[9]", "[23]")
    t = re.sub(r'\\[11\\]', '[7], [13]', t)
    return t'''

assert old_citation_funcs in code, "old_citation_funcs not found!"
code = code.replace(old_citation_funcs, new_citation_funcs, 1)

# 3. Update build_full_academic_references
old_refs_block = '''    # 1. Tài liệu thông tin doanh nghiệp & Website
    add_cat("1. Tài liệu thông tin doanh nghiệp & Website")
    add_ref("[1].", "Công ty Cổ phần Logistics U&I (2026).", "Trang chủ U&I Logistics", "https://unilogistics.vn/.")
    add_ref("[2].", "Công ty Cổ phần Logistics U&I (2026).", "Câu chuyện thương hiệu và Nền tảng phát triển", "https://unilogistics.vn/vi/cau-chuyen-thuong-hieu.")
    add_ref("[3].", "Công ty Cổ phần Logistics U&I (2026).", "Lịch sử hình thành và Các cột mốc phát triển", "https://unilogistics.vn/vi/gioi-thieu/lich-su-hinh-thanh.")
    add_ref("[4].", "Công ty Cổ phần Logistics U&I (2026).", "Dịch vụ đại lý thủ tục hải quan", "https://unilogistics.vn/vi/dich-vu/customs-brokerage-1.")
    add_ref("[5].", "Công ty Cổ phần Logistics U&I (2026).", "Dịch vụ kho vận và phân phối hàng hóa", "https://unilogistics.vn/vi/dich-vu/warehouse-service-2.")
    add_ref("[6].", "Công ty Cổ phần Logistics U&I (2026).", "Dịch vụ vận tải hàng hóa nội địa và Ứng dụng công nghệ GPS, TMS", "https://unilogistics.vn/vi/dich-vu/inland-transportation-3.")
    add_ref("[7].", "Công ty Cổ phần Logistics U&I (2026).", "Dịch vụ vận chuyển đường biển và hàng không quốc tế", "https://unilogistics.vn/vi/dich-vu/international-freight-forwarding-service-5.")
    add_ref("[8].", "Công ty Cổ phần Logistics U&I (2026).", "Mạng lưới đối tác và khách hàng tiêu biểu", "https://unilogistics.vn/vi/khach-hang/.")
    add_ref("[9].", "Công ty Cổ phần Logistics U&I (2026).", "Về chúng tôi: Tầm nhìn, Sứ mệnh và Triết lý phục vụ khách hàng", "https://unilogistics.vn/vi/gioi-thieu/ve-chung-toi.")
    add_ref("[10].", "Công ty Cổ phần Logistics U&I (2026).", "Hệ thống dịch vụ logistics tích hợp", "https://unilogistics.vn/vi/dich-vu.")

    # 2. Tiêu chuẩn quốc tế (Tiếng Anh)
    add_cat("2. Tiêu chuẩn quốc tế (Tiếng Anh)")
    add_ref("[11].", "International Organization for Standardization (2018).", "ISO 10002:2018 - Quality management - Customer satisfaction - Guidelines for complaints handling in organizations", "https://www.iso.org/standard/71580.html.")
    add_ref("[12].", "International Organization for Standardization (2018).", "ISO 10004:2018 - Quality management - Customer satisfaction - Guidelines for monitoring and measuring", "https://www.iso.org/standard/71582.html.")'''

new_refs_block = '''    # 1. Tiếng Việt
    add_cat("1. Tiếng Việt")
    add_ref("[1].", "Bộ Công Thương (2023).", "Báo cáo Logistics Việt Nam 2023 - Chuyển đổi số logistics", "NXB Công Thương, Hà Nội.")
    add_ref("[2].", "Quốc hội nước CHXHCN Việt Nam (2005).", "Luật Thương mại số 36/2005/QH11", "ngày 14 tháng 06 năm 2005, Hà Nội.")
    add_ref("[3].", "Chính phủ nước CHXHCN Việt Nam (2017).", "Nghị định số 163/2017/NĐ-CP quy định về kinh doanh dịch vụ logistics", "ngày 30 tháng 12 năm 2017, Hà Nội.")
    add_ref("[4].", "Đặng Đình Đào (2020).", "Giáo trình Quản trị Logistics", "NXB Tài chính, Hà Nội.")
    add_ref("[5].", "Hồ Thị Thu Hòa (2014).", "Mô hình đánh giá chất lượng dịch vụ logistics REPERIMP phù hợp với thực tế Việt Nam", "Tạp chí Giao thông Vận tải, số 3/2014, tr. 49-52.")
    add_ref("[6].", "Trịnh Thị Thu Hương (2020).", "Giáo trình Quản trị Logistics", "NXB Thông tin và Truyền thông, Hà Nội.")
    add_ref("[7].", "Tổng cục Tiêu chuẩn Đo lường Chất lượng (2018).", "TCVN ISO 10002:2018 (ISO 10002:2018) - Quản lý chất lượng - Sự hài lòng của khách hàng - Hướng dẫn xử lý khiếu nại trong tổ chức", "Bộ Khoa học và Công nghệ, Hà Nội.")
    add_ref("[8].", "Tổng cục Tiêu chuẩn Đo lường Chất lượng (2018).", "TCVN ISO 10004:2018 (ISO 10004:2018) - Quản lý chất lượng - Sự hài lòng của khách hàng - Hướng dẫn giám sát và đo lường", "Bộ Khoa học và Công nghệ, Hà Nội.")

    # 2. Tiếng Anh
    add_cat("2. Tiếng Anh")
    add_ref("[9].", "Davidow, M. (2003).", "Have You Heard the Word? The Effect of Word of Mouth on Complaint Resolution", "Journal of Service Research, 5(3), pp. 225-250. https://doi.org/10.1177/1094670502237737.")
    add_ref("[10].", "Homburg, C., & Fürst, A. (2005).", "How Organizational Complaint Handling Drives Customer Loyalty: An Analysis of the Mechanistic and the Organic Approach", "Journal of Marketing, 69(3), pp. 95-114. https://doi.org/10.1509/jmkg.69.3.95.66367.")
    add_ref("[11].", "Mentzer, J. T., Flint, D. J., & Hult, G. T. M. (2001).", "Logistics Service Quality as a Segment-Customized Process", "Journal of Marketing, 65(4), pp. 82-104. https://doi.org/10.1509/jmkg.65.4.82.18390.")
    add_ref("[12].", "Tax, S. S., Brown, S. W., & Chandrashekaran, M. (1998).", "Customer Evaluations of Service Complaint Experiences: Implications for Relationship Marketing", "Journal of Marketing, 62(2), pp. 60-76. https://doi.org/10.1177/002224299806200205.")
    add_ref("[13].", "International Organization for Standardization (2018).", "ISO 10002:2018 - Quality management - Customer satisfaction - Guidelines for complaints handling in organizations", "Geneva, Switzerland. https://www.iso.org/standard/71580.html.")
    add_ref("[14].", "International Organization for Standardization (2018).", "ISO 10004:2018 - Quality management - Customer satisfaction - Guidelines for monitoring and measuring", "Geneva, Switzerland. https://www.iso.org/standard/71582.html.")

    # 3. Website & Doanh nghiệp
    add_cat("3. Website & Doanh nghiệp")
    add_ref("[15].", "Công ty Cổ phần Logistics U&I (2026).", "Trang chủ U&I Logistics", "https://unilogistics.vn/.")
    add_ref("[16].", "Công ty Cổ phần Logistics U&I (2026).", "Câu chuyện thương hiệu và Nền tảng phát triển", "https://unilogistics.vn/vi/cau-chuyen-thuong-hieu.")
    add_ref("[17].", "Công ty Cổ phần Logistics U&I (2026).", "Lịch sử hình thành và Các cột mốc phát triển", "https://unilogistics.vn/vi/gioi-thieu/lich-su-hinh-thanh.")
    add_ref("[18].", "Công ty Cổ phần Logistics U&I (2026).", "Dịch vụ đại lý thủ tục hải quan", "https://unilogistics.vn/vi/dich-vu/customs-brokerage-1.")
    add_ref("[19].", "Công ty Cổ phần Logistics U&I (2026).", "Dịch vụ kho vận và phân phối hàng hóa", "https://unilogistics.vn/vi/dich-vu/warehouse-service-2.")
    add_ref("[20].", "Công ty Cổ phần Logistics U&I (2026).", "Dịch vụ vận tải hàng hóa nội địa và Ứng dụng công nghệ GPS, TMS", "https://unilogistics.vn/vi/dich-vu/inland-transportation-3.")
    add_ref("[21].", "Công ty Cổ phần Logistics U&I (2026).", "Dịch vụ vận chuyển đường biển và hàng không quốc tế", "https://unilogistics.vn/vi/dich-vu/international-freight-forwarding-service-5.")
    add_ref("[22].", "Công ty Cổ phần Logistics U&I (2026).", "Mạng lưới đối tác và khách hàng tiêu biểu", "https://unilogistics.vn/vi/khach-hang/.")
    add_ref("[23].", "Công ty Cổ phần Logistics U&I (2026).", "Về chúng tôi: Tầm nhìn, Sứ mệnh và Triết lý phục vụ khách hàng", "https://unilogistics.vn/vi/gioi-thieu/ve-chung-toi.")
    add_ref("[24].", "Công ty Cổ phần Logistics U&I (2026).", "Hệ thống dịch vụ logistics tích hợp", "https://unilogistics.vn/vi/dich-vu.")'''

assert old_refs_block in code, "old_refs_block not found!"
code = code.replace(old_refs_block, new_refs_block, 1)

# 4. Intercept P46 in Chapter 1 body loop
old_ch1_else = '''            else:
                np = doc.add_paragraph()
                np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                np.paragraph_format.line_spacing = 1.2
                np.paragraph_format.space_before = Pt(0)
                np.paragraph_format.space_after = Pt(6)
                np.paragraph_format.first_line_indent = Cm(1.27)
                copy_runs_with_format(src_p, np, default_size=13, is_ch1=True)'''

new_ch1_else = '''            else:
                if "Công ty tập trung vào các nhóm dịch vụ chính gồm đại lý thủ tục hải quan" in raw_text:
                    np = doc.add_paragraph()
                    np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    np.paragraph_format.line_spacing = 1.2
                    np.paragraph_format.space_before = Pt(0)
                    np.paragraph_format.space_after = Pt(6)
                    np.paragraph_format.first_line_indent = Cm(1.27)
                    r = np.add_run(
                        "Công ty tập trung vào các nhóm dịch vụ chính gồm đại lý thủ tục hải quan, kho vận và phân phối hàng hóa, vận tải nội địa, vận tải quốc tế bằng đường biển và đường hàng không. Đây là các dịch vụ cốt lõi phù hợp với danh mục ngành nghề kinh doanh dịch vụ logistics theo quy định tại Điều 233 Luật Thương mại 2005 [2] và Nghị định 163/2017/NĐ-CP [3], đồng thời phản ánh mô hình quản trị chuỗi cung ứng logistics tích hợp [4], [6]."
                    )
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(13)
                    r.font.color.rgb = BLACK_COLOR
                    continue

                np = doc.add_paragraph()
                np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                np.paragraph_format.line_spacing = 1.2
                np.paragraph_format.space_before = Pt(0)
                np.paragraph_format.space_after = Pt(6)
                np.paragraph_format.first_line_indent = Cm(1.27)
                copy_runs_with_format(src_p, np, default_size=13, is_ch1=True)'''

assert old_ch1_else in code, "old_ch1_else not found!"
code = code.replace(old_ch1_else, new_ch1_else, 1)

# 5. Intercept 9 target paragraphs in Chapter 2 & 3 body loop
old_ch23_else = '''            else:
                np = doc.add_paragraph()
                np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                np.paragraph_format.line_spacing = 1.2
                np.paragraph_format.space_before = Pt(0)
                np.paragraph_format.space_after = Pt(6)
                np.paragraph_format.first_line_indent = Cm(1.27)
                copy_runs_with_format(src_p, np, default_size=13, is_ch23=True)'''

new_ch23_else = '''            else:
                if "Trong phạm vi nghiên cứu, Công ty cung cấp thông tin về 05 trường hợp khiếu nại được mã hóa từ KN01 đến KN05" in raw_text:
                    np = doc.add_paragraph()
                    np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    np.paragraph_format.line_spacing = 1.2
                    np.paragraph_format.space_before = Pt(0)
                    np.paragraph_format.space_after = Pt(6)
                    np.paragraph_format.first_line_indent = Cm(1.27)
                    r = np.add_run(
                        "Trong phạm vi nghiên cứu, Công ty cung cấp thông tin về 05 trường hợp khiếu nại được mã hóa từ KN01 đến KN05, thuộc hai nhóm nghiệp vụ chính là vận chuyển và khai báo hải quan. Theo các nghiên cứu thực nghiệm về quản trị dịch vụ logistics, khiếu nại phát sinh khi có sự sai lệch giữa kỳ vọng và chất lượng dịch vụ thực tế mà khách hàng nhận được [5], [11]. Về mặt lý thuyết, lý thuyết công bằng (Justice Theory) chỉ ra rằng đánh giá của khách hàng đối với việc giải quyết khiếu nại được định hình bởi sự công bằng phân phối, công bằng thủ tục và công bằng tương tác [12]. Các trường hợp này được nhóm tác giả tiếp cận và tổng hợp nhằm phục vụ việc phân tích thực trạng quy trình giải quyết khiếu nại của Công ty. Việc tổng hợp các trường hợp theo từng nhóm nghiệp vụ giúp làm rõ những nội dung khách hàng phản ánh, đặc điểm của từng tình huống cũng như các bộ phận và loại thông tin cần được kiểm tra trong quá trình xử lý. Do đó, 05 trường hợp được sử dụng làm cơ sở minh họa cho các tình huống khiếu nại và cách thức xử lý trong phạm vi nghiên cứu."
                    )
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(13)
                    r.font.color.rgb = BLACK_COLOR
                    continue

                elif "Nội dung cần đối chiếu đối với nhóm vận chuyển chủ yếu gồm thời gian phương tiện đã được xác nhận" in raw_text:
                    np = doc.add_paragraph()
                    np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    np.paragraph_format.line_spacing = 1.2
                    np.paragraph_format.space_before = Pt(0)
                    np.paragraph_format.space_after = Pt(6)
                    np.paragraph_format.first_line_indent = Cm(1.27)
                    r = np.add_run(
                        "Nội dung cần đối chiếu đối với nhóm vận chuyển chủ yếu gồm thời gian phương tiện đã được xác nhận, thời gian thực tế và diễn biến điều độ. Biểu hiện phương tiện đến không đúng thời gian dự kiến có thể xuất hiện tại những khâu khác nhau như lấy hàng hoặc giao hàng, vì vậy cần phân biệt thời điểm phát sinh và nội dung ảnh hưởng trong từng tình huống. Theo nghiên cứu của Davidow (2003), tính kịp thời (Timeliness) là một trong những chiều kích phản hồi quan trọng nhất tác động trực tiếp đến sự thỏa mãn của khách hàng sau khiếu nại [9]. Theo thông tin được U&I Logistics công bố và được dẫn trong tài liệu nghiên cứu, hoạt động vận tải của Công ty được hỗ trợ bởi GPS, TMS và ứng dụng dành cho tài xế, là những công cụ cung cấp thông tin phục vụ đối chiếu hành trình và tình trạng thực hiện vận chuyển [20]. Việc đề cập các công cụ này chỉ nhằm làm rõ nguồn thông tin phù hợp với đặc điểm nghiệp vụ, không xác nhận chúng đã được sử dụng trong từng tình huống minh họa."
                    )
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(13)
                    r.font.color.rgb = BLACK_COLOR
                    continue

                elif "Phương án phải được trình cấp có thẩm quyền xem xét trước khi triển khai. Cơ chế phê duyệt giúp kiểm soát quyết định" in raw_text:
                    np = doc.add_paragraph()
                    np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    np.paragraph_format.line_spacing = 1.2
                    np.paragraph_format.space_before = Pt(0)
                    np.paragraph_format.space_after = Pt(6)
                    np.paragraph_format.first_line_indent = Cm(1.27)
                    r = np.add_run(
                        "Phương án phải được trình cấp có thẩm quyền xem xét trước khi triển khai. Cơ chế phê duyệt giúp kiểm soát quyết định có ảnh hưởng đến chi phí, uy tín hoặc cam kết với khách hàng. Thông tin doanh nghiệp cho biết khách hàng thông thường vẫn tiếp tục sử dụng dịch vụ sau xử lý, là tín hiệu tích cực về khả năng duy trì quan hệ, dù chưa có tỷ lệ cụ thể để lượng hóa. Trên website chính thức, U&I Logistics công bố định hướng đặt quyền lợi khách hàng lên trước [23]. Ở góc độ quản trị, việc giải quyết thỏa đáng khiếu nại không chỉ giảm thiểu tỷ lệ rời bỏ mà còn chuyển hóa khách hàng bất mãn thành khách hàng trung thành thông qua cơ chế phản hồi linh hoạt và trao quyền cho nhân viên xử lý [10], [12]."
                    )
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(13)
                    r.font.color.rgb = BLACK_COLOR
                    continue

                elif "Quy trình đã yêu cầu xem xét hành động khắc phục và phòng ngừa nhưng chưa mô tả đầy đủ cơ chế tổng hợp bài học" in raw_text:
                    np = doc.add_paragraph()
                    np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    np.paragraph_format.line_spacing = 1.2
                    np.paragraph_format.space_before = Pt(0)
                    np.paragraph_format.space_after = Pt(6)
                    np.paragraph_format.first_line_indent = Cm(1.27)
                    r = np.add_run(
                        "Quy trình đã yêu cầu xem xét hành động khắc phục và phòng ngừa nhưng chưa mô tả đầy đủ cơ chế tổng hợp bài học, lựa chọn vấn đề ưu tiên, phân công người theo dõi và đánh giá hiệu lực sau một khoảng thời gian. Vì vậy, kinh nghiệm từ từng vụ việc có nguy cơ dừng ở hồ sơ thay vì chuyển thành điều chỉnh có thể kiểm chứng trong hoạt động vận hành. TCVN ISO 10002:2018 (ISO 10002:2018) cũng xem việc rà soát hiệu lực và hiệu quả của quá trình xử lý là một nội dung quan trọng [7], [13]. Bên cạnh đó, việc thiếu hụt hệ thống đo lường và theo dõi định lượng sự hài lòng của khách hàng sau giải quyết khiếu nại theo hướng dẫn của TCVN ISO 10004:2018 (ISO 10004:2018) [8], [14] khiến doanh nghiệp chưa nắm bắt được chỉ số thỏa mãn thực tế của khách hàng."
                    )
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(13)
                    r.font.color.rgb = BLACK_COLOR
                    continue

                elif "Bên cạnh những hạn chế của quy trình hiện tại, việc hoàn thiện quy trình giải quyết khiếu nại còn xuất phát từ nhu cầu nâng cao chất lượng dịch vụ" in raw_text:
                    np = doc.add_paragraph()
                    np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    np.paragraph_format.line_spacing = 1.2
                    np.paragraph_format.space_before = Pt(0)
                    np.paragraph_format.space_after = Pt(6)
                    np.paragraph_format.first_line_indent = Cm(1.27)
                    r = np.add_run(
                        "Bên cạnh những hạn chế của quy trình hiện tại, việc hoàn thiện quy trình giải quyết khiếu nại còn xuất phát từ nhu cầu nâng cao chất lượng dịch vụ logistics và đáp ứng định hướng chuyển đổi số của ngành [1], [5]. Chuẩn hóa quy trình theo chu trình PDCA và nguyên tắc cốt lõi của tiêu chuẩn TCVN ISO 10002:2018 [7], [13] giúp Công ty phản hồi kịp thời, minh bạch và có hệ thống. Bên cạnh đó, việc ghi nhận phản hồi và mức độ hài lòng sau giải quyết giúp đánh giá kết quả xử lý từ góc độ khách hàng. Thông tin về nguyên nhân, quá trình và kết quả xử lý cũng cần được lưu trữ có hệ thống nhằm hỗ trợ tra cứu, kiểm soát và nhận diện các vấn đề tái diễn, từ đó đề xuất biện pháp khắc phục, phòng ngừa và nâng cao chất lượng dịch vụ."
                    )
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(13)
                    r.font.color.rgb = BLACK_COLOR
                    continue

                elif "Sau khi hoàn tất bước xem xét sơ bộ, khiếu nại được phân loại theo nhóm dịch vụ phát sinh" in raw_text:
                    np = doc.add_paragraph()
                    np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    np.paragraph_format.line_spacing = 1.2
                    np.paragraph_format.space_before = Pt(0)
                    np.paragraph_format.space_after = Pt(6)
                    np.paragraph_format.first_line_indent = Cm(1.27)
                    r = np.add_run(
                        "Sau khi hoàn tất bước xem xét sơ bộ, khiếu nại được phân loại theo nhóm dịch vụ phát sinh để xác định nội dung kiểm tra và các bộ phận hoặc đơn vị có liên quan. Để bảo đảm tính liên tục giữa các công đoạn và hạn chế thời gian chờ trong quá trình xử lý, thời hạn thực hiện bước này được quy định trong vòng 0,5 ngày làm việc kể từ khi hoàn tất xem xét sơ bộ. Việc thiết lập thời hạn cụ thể giúp kiểm soát tiến độ chuyển tiếp giữa các bước, bảo đảm chiều kích kịp thời (Timeliness) theo nghiên cứu của Davidow (2003) [9], tạo điều kiện để các bộ phận liên quan chủ động tiếp nhận thông tin và triển khai công việc tiếp theo. Mốc thời gian này cũng phù hợp với đặc điểm của hoạt động phân loại, bởi công việc chủ yếu dựa trên thông tin đã được ghi nhận và kết quả xem xét sơ bộ, tập trung vào việc xác định nhóm dịch vụ và phạm vi kiểm tra ban đầu, thay vì tiến hành xác minh chi tiết hoặc phân tích nguyên nhân khiếu nại. Qua đó, thời gian xử lý được kiểm soát chặt chẽ hơn mà vẫn bảo đảm sự phân định rõ ràng giữa hoạt động phân loại và hoạt động kiểm tra, xác minh."
                    )
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(13)
                    r.font.color.rgb = BLACK_COLOR
                    continue

                elif "Sau khi hoàn tất việc giải quyết khiếu nại, Phòng Kinh doanh thực hiện đánh giá kết quả xử lý thông qua Phiếu đánh giá" in raw_text:
                    np = doc.add_paragraph()
                    np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    np.paragraph_format.line_spacing = 1.2
                    np.paragraph_format.space_before = Pt(0)
                    np.paragraph_format.space_after = Pt(6)
                    np.paragraph_format.first_line_indent = Cm(1.27)
                    r = np.add_run(
                        "Sau khi hoàn tất việc giải quyết khiếu nại, Phòng Kinh doanh thực hiện đánh giá kết quả xử lý thông qua Phiếu đánh giá quá trình giải quyết khiếu nại của khách hàng được thiết kế theo khung phương pháp luận của tiêu chuẩn TCVN ISO 10004:2018 [8], [14]. Phiếu được gửi cho khách hàng nhằm ghi nhận trực tiếp ý kiến và mức độ hài lòng đối với quá trình xử lý. Nội dung đánh giá tập trung vào các tiêu chí như quá trình tiếp nhận, thời gian phản hồi, cách thức giải quyết, mức độ đáp ứng yêu cầu và đánh giá chung của khách hàng. Kết quả được tổng hợp để theo dõi chất lượng xử lý khiếu nại."
                    )
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(13)
                    r.font.color.rgb = BLACK_COLOR
                    continue

                elif "Phòng Kinh doanh là đầu mối tổ chức và kiểm soát quy trình, chịu trách nhiệm tiếp nhận, xem xét sơ bộ" in raw_text:
                    np = doc.add_paragraph()
                    np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    np.paragraph_format.line_spacing = 1.2
                    np.paragraph_format.space_before = Pt(0)
                    np.paragraph_format.space_after = Pt(6)
                    np.paragraph_format.first_line_indent = Cm(1.27)
                    r = np.add_run(
                        "Phòng Kinh doanh là đầu mối tổ chức và kiểm soát quy trình, chịu trách nhiệm tiếp nhận, xem xét sơ bộ, phân loại khiếu nại, điều phối các bộ phận liên quan, theo dõi tiến độ và tổng hợp kết quả xử lý. Nhân viên kinh doanh trực tiếp ghi nhận thông tin trên BM01-QT06/KD, trao đổi với khách hàng, cập nhật tình trạng xử lý, phản hồi kết quả và thu thập ý kiến sau giải quyết. Các phòng ban liên quan chịu trách nhiệm kiểm tra, cung cấp thông tin và xác định nguyên nhân thuộc phạm vi chuyên môn; trong đó bộ phận Hải quan kiểm tra hồ sơ, chứng từ và thông tin khai báo, còn bộ phận vận chuyển kiểm tra tình trạng lô hàng và quá trình vận chuyển. Phương án giải quyết và bồi thường được xây dựng căn cứ trên các quy định về giới hạn trách nhiệm của thương nhân dịch vụ logistics theo Luật Thương mại 2005 [2] và Nghị định 163/2017/NĐ-CP [3]. Đồng thời, công ty vận dụng cơ chế phân quyền ủy quyền xử lý nhanh đối với các sự vụ có giá trị nhỏ nhằm nâng cao sự hài lòng và công bằng cảm nhận của khách hàng [10], [12]."
                    )
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(13)
                    r.font.color.rgb = BLACK_COLOR
                    continue

                elif "Trước khi áp dụng chính thức, Phòng Kinh doanh tổ chức hướng dẫn cho nhân viên kinh doanh" in raw_text:
                    np = doc.add_paragraph()
                    np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    np.paragraph_format.line_spacing = 1.2
                    np.paragraph_format.space_before = Pt(0)
                    np.paragraph_format.space_after = Pt(6)
                    np.paragraph_format.first_line_indent = Cm(1.27)
                    r = np.add_run(
                        "Trước khi áp dụng chính thức, Phòng Kinh doanh tổ chức hướng dẫn và đào tạo kỹ năng mềm, thái độ thấu cảm và kiến thức quản trị xung đột logistics [4], [6] cho nhân viên kinh doanh và đại diện các bộ phận có liên quan nhằm bảo đảm nhân viên hiểu rõ trình tự thực hiện và trách nhiệm của mình trong quy trình mới. Nội dung hướng dẫn tập trung vào những nội dung được bổ sung so với quy trình hiện tại, gồm cách phân loại khiếu nại theo nhóm dịch vụ, xác định mức độ ưu tiên, cập nhật thông tin trên BM01-QT06/KD, phối hợp với các bộ phận liên quan và thu thập phản hồi của khách hàng sau khi hoàn tất giải quyết."
                    )
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(13)
                    r.font.color.rgb = BLACK_COLOR
                    continue

                np = doc.add_paragraph()
                np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                np.paragraph_format.line_spacing = 1.2
                np.paragraph_format.space_before = Pt(0)
                np.paragraph_format.space_after = Pt(6)
                np.paragraph_format.first_line_indent = Cm(1.27)
                copy_runs_with_format(src_p, np, default_size=13, is_ch23=True)'''

assert old_ch23_else in code, "old_ch23_else not found!"
code = code.replace(old_ch23_else, new_ch23_else, 1)

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("SUCCESS: Code updated cleanly!")
