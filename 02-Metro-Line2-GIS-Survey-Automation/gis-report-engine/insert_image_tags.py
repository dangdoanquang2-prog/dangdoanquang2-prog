import docx

def insert_tags():
    doc = docx.Document('Template_BaoCao_V2.docx')
    
    # 1. Tìm vị trí "Hình MA_GA_SHORT 2" (Bản đồ tổng quát)
    for p in doc.paragraphs:
        if 'phát hiện tổng quát' in p.text:
            # Chèn 1 đoạn văn chứa Tag ngay trước đoạn caption này
            p.insert_paragraph_before('{{ ANH_TONG_QUAT }}')
            print("Đã chèn {{ ANH_TONG_QUAT }} thành công!")
            
    # 2. Tìm vị trí "LỐI VÀO GA" trong bảng
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    if 'LỐI VÀO GA' in p.text:
                        p.insert_paragraph_before('{{ ANH_LOI_VAO }}')
                        print("Đã chèn {{ ANH_LOI_VAO }} vào bảng thành công!")
                        break

    doc.save('Template_BaoCao_V2.docx')
    print("Xong!")

if __name__ == '__main__':
    insert_tags()
