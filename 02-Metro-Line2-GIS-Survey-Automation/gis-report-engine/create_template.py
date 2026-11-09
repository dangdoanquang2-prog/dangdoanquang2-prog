import docx
import re

def replace_in_runs(paragraph, replacements):
    # Thay thế văn bản trong các đoạn (paragraph)
    # Lưu ý: Việc gán lại paragraph.text sẽ xóa các định dạng (in đậm, in nghiêng) cục bộ trong đoạn đó,
    # nhưng nó đảm bảo thay thế được toàn bộ chuỗi.
    text = paragraph.text
    changed = False
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            changed = True
    if changed:
        paragraph.text = text

def replace_in_doc(doc_path, output_path):
    doc = docx.Document(doc_path)
    
    # Danh sách các từ cần thay thế thành biến
    replacements = {
        "TAO ĐÀN": "{{ TEN_GA_UPPER }}",
        "Tao Đàn": "{{ TEN_GA }}",
        "S2 ": "{{ MA_GA }} ",
        " S2\n": " {{ MA_GA }}\n",
        "S2": "{{ MA_GA }}", # Xử lý cẩn thận để không thay nhầm
        "Km1+261.5": "{{ LY_TRINH }}",
        "TD1": "{{ MA_GA_SHORT }}1",
        "TD2": "{{ MA_GA_SHORT }}2",
        "TD3": "{{ MA_GA_SHORT }}3",
        "TD4": "{{ MA_GA_SHORT }}4",
        "TD5": "{{ MA_GA_SHORT }}5",
        "TD6": "{{ MA_GA_SHORT }}6",
        "Bảng TD": "Bảng {{ MA_GA_SHORT }}",
        "Hình TD": "Hình {{ MA_GA_SHORT }}",
    }
    
    # Cập nhật cẩn thận để tránh dính chữ (vd "TD" trong chữ khác)
    # Ta sẽ dùng replace cơ bản, người dùng có thể chỉnh sửa thêm sau.

    print("Đang xử lý các Đoạn văn (Paragraphs)...")
    for p in doc.paragraphs:
        replace_in_runs(p, replacements)
        
    print("Đang xử lý các Bảng biểu (Tables)...")
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    replace_in_runs(p, replacements)
                    
    doc.save(output_path)
    print(f"Thành công! Đã lưu file Template mới: {output_path}")

if __name__ == '__main__':
    input_file = 'APPENDIX 4 _1- GA TAO DAN 30 -10 VN.docx'
    output_file = 'Template_BaoCao.docx'
    replace_in_doc(input_file, output_file)
