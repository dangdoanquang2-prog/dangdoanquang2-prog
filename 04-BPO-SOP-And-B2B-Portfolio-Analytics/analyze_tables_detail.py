import docx
from docx.oxml.ns import qn

doc = docx.Document("BÀI MẪU.docx")

lines = []
lines.append("=================== PHÂN TÍCH BẢNG BIỂU (TABLES) TRONG BÀI MẪU.DOCX ===================")
lines.append(f"Tổng số bảng tìm thấy: {len(doc.tables)}\n")

for idx, table in enumerate(doc.tables):
    lines.append(f"--- BẢNG {idx+1} ---")
    lines.append(f"Số hàng: {len(table.rows)}, Số cột: {len(table.columns)}")
    lines.append(f"Alignment: {table.alignment}")
    
    # Check header row shading & cell XML
    first_row = table.rows[0]
    shading_list = []
    for c in first_row.cells:
        shd = c._tc.get_or_add_tcPr().find(qn('w:shd'))
        if shd is not None:
            shading_list.append(shd.get(qn('w:fill')))
        else:
            shading_list.append("None")
    lines.append(f"Màu nền Header (Shading): {shading_list}")

    # Check cell text samples
    lines.append("Hàng 1 (Header): " + " | ".join(c.text.replace("\n", " ").strip() for c in first_row.cells))
    if len(table.rows) > 1:
        lines.append("Hàng 2 (Data): " + " | ".join(c.text.replace("\n", " ").strip() for c in table.rows[1].cells))
    lines.append("\n")

with open("tables_detailed_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Saved tables_detailed_analysis.txt!")
