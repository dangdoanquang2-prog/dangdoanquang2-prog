import docx
import sys
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document(r'd:\baocaotudong\output\BC_KhaoSat_HienTrang_Ga_ST01_PhanVanHon.docx')
print('Total paragraphs:', len(doc.paragraphs))
print('Total tables:', len(doc.tables))

headings = [p.text for p in doc.paragraphs if p.text.startswith('MỤC')]
print('\nHeadings found:')
for h in headings:
    print(' -', h)

captions = [p.text for p in doc.paragraphs if 'Hình' in p.text]
for t in doc.tables:
    for r in t.rows:
        for c in r.cells:
            for p in c.paragraphs:
                if 'Hình' in p.text:
                    captions.append(p.text.split('\n')[0])

print('\nCaptions found:')
for c in captions:
    print(' -', c)

page_breaks = [p for p in doc.paragraphs if any('w:br' in r._r.xml and 'page' in r._r.xml for r in p.runs)]
print(f'\nTotal page breaks: {len(page_breaks)}')

non_tnr = []
for p in doc.paragraphs:
    for r in p.runs:
        if r.font.name != 'Times New Roman' and r.text.strip():
            non_tnr.append((r.text[:20], r.font.name))
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    if r.font.name != 'Times New Roman' and r.text.strip():
                        non_tnr.append((r.text[:20], r.font.name))

print(f'Total non-Times New Roman runs: {len(non_tnr)}')
if non_tnr:
    print('Non-TNR sample:', non_tnr[:5])
