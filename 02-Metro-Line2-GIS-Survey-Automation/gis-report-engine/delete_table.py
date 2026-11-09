import docx

def modify_template():
    doc = docx.Document('Template_BaoCao_V2.docx')
    
    # 1. Tìm bảng chứa "PW1" (bảng chi tiết lối đi)
    table_to_delete = None
    for t in doc.tables:
        # Kiểm tra nội dung của bảng có chữ PW1 không
        text_in_table = " ".join([c.text for row in t.rows for c in row.cells])
        if 'PW1' in text_in_table and 'PW8' in text_in_table:
            table_to_delete = t
            break
            
    if table_to_delete:
        print("Đã tìm thấy Bảng lối đi (chứa PW1 - PW8)!")
        
        # 2. Thêm thẻ Tag ngay trước bảng này
        from docx.oxml import OxmlElement
        p = OxmlElement('w:p')
        table_to_delete._element.addprevious(p)
        new_p = docx.text.paragraph.Paragraph(p, doc._body)
        new_p.add_run('{{ KET_QUA_LOI_DI }}')
        print("Đã chèn thẻ {{ KET_QUA_LOI_DI }} thành công.")
        
        # 3. Xóa bảng
        tbl = table_to_delete._element
        tbl.getparent().remove(tbl)
        print("Đã xóa Bảng 8 lối đi của Tao Đàn.")
    else:
        print("Không tìm thấy Bảng lối đi.")

    doc.save('Template_BaoCao_V3.docx')
    print("Xong! Đã lưu thành Template_BaoCao_V3.docx")

if __name__ == '__main__':
    modify_template()
