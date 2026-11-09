import docx

def prepare_template():
    doc = docx.Document('Template_BaoCao.docx')
    
    # Thêm một phần mới vào cuối tài liệu để kiểm chứng việc chèn dữ liệu động & ảnh
    doc.add_page_break()
    p_h1 = doc.add_paragraph('PHẦN KIỂM CHỨNG DỮ LIỆU ĐỘNG TỪ APP (AUTO-GENERATED)')
    p_h1.runs[0].bold = True
    
    doc.add_paragraph("Đây là phần nội dung được App tự động tạo ra dựa trên tọa độ GIS và dữ liệu nhập liệu từ Web Form:")
    
    p_h2_1 = doc.add_paragraph('1. Kết quả quét Tiện ích đô thị (OSM)')
    p_h2_1.runs[0].bold = True
    p_tien_ich = doc.add_paragraph()
    p_tien_ich.add_run('{{ MO_TA_TIEN_ICH }}').bold = True
    
    p_h2_2 = doc.add_paragraph('2. Bản đồ GIS Bán kính 1000m')
    p_h2_2.runs[0].bold = True
    doc.add_paragraph('{{ BANDO_1000M }}')
    
    p_h2_3 = doc.add_paragraph('3. Dữ liệu từ Form Khảo Sát Hiện Trường')
    p_h2_3.runs[0].bold = True
    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Tiêu chí Khảo sát'
    hdr_cells[1].text = 'Kết quả nhập từ Web'
    
    row_cells = table.add_row().cells
    row_cells[0].text = 'Bề rộng mặt đường (m)'
    row_cells[1].text = '{{ BE_RONG_DUONG }}'
    
    row_cells = table.add_row().cells
    row_cells[0].text = 'Bề rộng vỉa hè (m)'
    row_cells[1].text = '{{ BE_RONG_VIA_HE }}'
    
    row_cells = table.add_row().cells
    row_cells[0].text = 'Tình trạng vỉa hè'
    row_cells[1].text = '{{ TINH_TRANG_VIA_HE }}'
    
    row_cells = table.add_row().cells
    row_cells[0].text = 'Đề xuất Vị trí Cổng EN1'
    row_cells[1].text = '{{ DE_XUAT_EN1 }}'
    
    # Save the updated template
    doc.save('Template_BaoCao_V2.docx')
    print("Đã tạo thành công Template_BaoCao_V2.docx với các thẻ dữ liệu động!")

if __name__ == '__main__':
    prepare_template()
