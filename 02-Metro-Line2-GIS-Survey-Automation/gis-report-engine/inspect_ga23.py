import openpyxl, sys, json

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook('Ga 23.xlsx', data_only=True)

print("="*80)
print("PHÂN TÍCH CHI TIẾT FILE GA 23.XLSX")
print("="*80)

for sname in wb.sheetnames:
    ws = wb[sname]
    headers = [str(ws.cell(1, c).value or '').strip() for c in range(1, ws.max_column + 1)]
    print(f"\n>>> SHEET: [{sname}] - Rows: {ws.max_row-1}")
    
    rows_data = []
    for r in range(2, ws.max_row + 1):
        row_dict = {}
        for c in range(1, ws.max_column + 1):
            val = ws.cell(r, c).value
            if val is not None and str(val).strip() != '':
                row_dict[headers[c-1]] = str(val).strip()
        if row_dict:
            rows_data.append(row_dict)
            
    print(f"Số dòng có dữ liệu: {len(rows_data)}")
    for idx, rd in enumerate(rows_data, 1):
        print(f"\n  --- Dòng {idx} ---")
        for k, v in list(rd.items())[:10]:
            print(f"    * {k}: {v}")
        if len(rd) > 10:
            print(f"    * ... và {len(rd)-10} trường khác")
