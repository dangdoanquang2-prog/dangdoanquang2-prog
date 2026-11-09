import openpyxl, sys, json

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook('Ga 23.xlsx', data_only=True)

def dump_sheet(sname):
    ws = wb[sname]
    headers = [str(ws.cell(1, c).value or '').strip() for c in range(1, ws.max_column + 1)]
    print(f"\n=================== SHEET: {sname} ===================")
    for r in range(2, ws.max_row + 1):
        row_dict = {}
        for c in range(1, ws.max_column + 1):
            val = ws.cell(r, c).value
            if val is not None and str(val).strip() != '':
                row_dict[headers[c-1]] = str(val).strip()
        if row_dict:
            print(f"\n[Dòng {r}]")
            for k, v in row_dict.items():
                print(f"  * {k}: {v}")

for sname in wb.sheetnames:
    if sname != 'KHẢO SÁT TIẾP CẬN HIỆN TRƯỜNG N': # already dumped
        dump_sheet(sname)
