import sys
import os
from docx import Document

sys.stdout.reconfigure(encoding='utf-8')
docx_path = r"D:\baocaotudong\08. Phat sinh-thu hut\Bao_cao_Tong_hop_Nhiem_vu_8_Diem_phat_sinh_nhu_cau_lon.docx"
doc = Document(docx_path)

print(f"=== CHI TIẾT TẤT CẢ CÁC BẢNG TRONG FILE MẪU ===")
for t_idx, tbl in enumerate(doc.tables):
    rows = len(tbl.rows)
    cols = len(tbl.columns)
    print(f"\n--- BẢNG {t_idx+1}: {rows} hàng x {cols} cột ---")
    for r_idx in range(min(rows, 6)):
        cells = [c.text.strip().replace('\n', ' ') for c in tbl.rows[r_idx].cells]
        # dedup
        dedup = []
        for ct in cells:
            if not dedup or ct != dedup[-1]:
                dedup.append(ct)
        print(f"  R{r_idx}: " + " | ".join(dedup[:6]))
