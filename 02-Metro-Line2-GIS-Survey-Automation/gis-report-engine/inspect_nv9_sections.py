import docx

doc = docx.Document('NHIEM VU 9 PHIEU KHAO SAT HIEN TRANG TIEP CAN VA TRUNG CHUYEN KHU VUC GA DUONG SAT DO THI.docx')

with open('nv9_structure.txt', 'w', encoding='utf-8') as f:
    f.write("=== CẤU TRÚC PHIẾU KHẢO SÁT NHIỆM VỤ 9 (MỤC A ĐẾN MỤC M) ===\n\n")
    for i, p in enumerate(doc.paragraphs):
        txt = p.text.strip()
        if txt:
            for c in 'ABCDEFGHIJKLM':
                if txt.startswith(f"{c}."):
                    f.write(f"[{c}] {txt}\n")
    
    f.write("\n=== DANH SÁCH BẢNG TRONG FILE NV9 ===\n")
    for idx, table in enumerate(doc.tables):
        f.write(f"\n--- Bảng {idx+1} ({len(table.rows)} hàng x {len(table.columns)} cột) ---\n")
        for r_idx in range(min(3, len(table.rows))):
            row_txt = " | ".join([cell.text.strip().replace('\n', ' ') for cell in table.rows[r_idx].cells])
            f.write(f"  Row {r_idx+1}: {row_txt}\n")

print("Written nv9_structure.txt successfully!")
