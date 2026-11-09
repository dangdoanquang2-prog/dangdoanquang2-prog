import os
import sys
import docx

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = r"d:\baocaotudong\output"

STATIONS = [
    ("ST01", "PhanVanHon"),
    ("ST02", "DongHungThuan"),
    ("ST03", "AnSuong"),
    ("ST04", "NguyenAnhThu"),
    ("ST05", "NguyenThiSoc"),
    ("ST06", "BaTrieu"),
    ("ST07", "LyThuongKiet"),
    ("ST08", "NguyenThiNuoi"),
    ("ST09", "VongcungTayBac2"),
    ("ST10", "VanhDai3"),
    ("ST11", "AnHa"),
    ("ST12", "TanPhuTrung"),
    ("ST13", "HuongLo2"),
    ("ST14", "DaoThiKiem"),
    ("ST15", "LeMinhNhut"),
    ("ST16", "TanThongHoi"),
    ("ST17", "TranTuBinh"),
    ("ST18", "HuynhVanCo"),
    ("ST19", "CuChi"),
    ("ST20", "BVCuChi"),
    ("ST21", "NguyenThiRanh"),
    ("ST22", "TanAnHoi"),
    ("ST23", "BaSa"),
    ("ST24", "PhuocHiep"),
    ("ST25", "TinhLo7"),
    ("ST26", "ThaiMy")
]

FORBIDDEN_WORDS = ["bóc tách", "file ga", ".jpg", "_vinh", "nhiệm vụ 9", "phụ lục 4"]

def check_report(st_code, ascii_name):
    fname = f"BC_KhaoSat_HienTrang_Ga_{st_code}_{ascii_name}.docx"
    fpath = os.path.join(OUTPUT_DIR, fname)
    if not os.path.exists(fpath):
        return {"status": "MISSING", "path": fpath}
    
    size_mb = os.path.getsize(fpath) / (1024 * 1024)
    doc = docx.Document(fpath)
    
    # 1. Page breaks
    page_breaks = [p for p in doc.paragraphs if any('w:br' in r._r.xml and 'page' in r._r.xml for r in p.runs)]
    
    # 2. Headings
    headings = [p.text.strip() for p in doc.paragraphs if p.text.strip().startswith("MỤC")]
    expected_headings_prefix = f"MỤC {st_code}."
    all_headings_ok = all(h.startswith(expected_headings_prefix) for h in headings) and len(headings) >= 8
    
    # 3. Captions
    captions = []
    for p in doc.paragraphs:
        if "Hình" in p.text:
            captions.append(p.text.strip())
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    for line in p.text.split("\n"):
                        if "Hình" in line and not line.startswith("3.") and not line.startswith("2.") and "xung đột" not in line.lower():
                            captions.append(line.strip())
                            
    expected_cap_prefix = f"Hình {st_code}."
    all_captions_ok = all(c.startswith(expected_cap_prefix) for c in captions if c.startswith("Hình"))
    
    # 4. Font check
    non_tnr = 0
    for p in doc.paragraphs:
        for r in p.runs:
            if r.font.name != "Times New Roman" and r.text.strip():
                non_tnr += 1
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for r in p.runs:
                        if r.font.name != "Times New Roman" and r.text.strip():
                            non_tnr += 1
                            
    # 5. Forbidden words
    found_forbidden = []
    for p in doc.paragraphs:
        t_low = p.text.lower()
        for fw in FORBIDDEN_WORDS:
            if fw in t_low:
                found_forbidden.append(fw)
                
    return {
        "status": "OK",
        "name": fname,
        "size_mb": size_mb,
        "page_breaks": len(page_breaks),
        "headings_count": len(headings),
        "headings_ok": all_headings_ok,
        "captions_count": len(captions),
        "captions_ok": all_captions_ok,
        "non_tnr": non_tnr,
        "forbidden": list(set(found_forbidden))
    }

print("=" * 80)
print(f"VERIFYING ALL 26 REPORTS IN {OUTPUT_DIR}")
print("=" * 80)

results = []
all_passed = True
for code, name in STATIONS:
    res = check_report(code, name)
    results.append((code, name, res))
    if res.get("status") != "OK" or res.get("page_breaks") != 9 or not res.get("headings_ok") or not res.get("captions_ok") or res.get("non_tnr") != 0 or len(res.get("forbidden", [])) > 0:
        all_passed = False
    status_str = "PASS" if res.get("status") == "OK" and res.get("page_breaks") == 9 and res.get("non_tnr") == 0 and res.get("headings_ok") and res.get("captions_ok") else "FAIL"
    tnr_str = "100%" if res.get('non_tnr') == 0 else f"{res.get('non_tnr')} err"
    print(f"[{code}] {name:20s} | Status: {status_str} | Size: {res.get('size_mb', 0):.2f}MB | Breaks: {res.get('page_breaks', 0)}/9 | TNR: {tnr_str} | Headings: {res.get('headings_count', 0)} | Captions: {res.get('captions_count', 0)}")

print("=" * 80)
if all_passed:
    print("ALL 26 REPORTS PASSED 100% QUALITY AND COMPLIANCE CHECKS!")
else:
    print("SOME CHECKS REQUIRE ATTENTION.")
print("=" * 80)
