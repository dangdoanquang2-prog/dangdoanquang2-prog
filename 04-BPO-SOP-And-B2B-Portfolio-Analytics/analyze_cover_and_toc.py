import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

doc = docx.Document("BÀI MẪU.docx")

lines = []
lines.append("=================== 1. PHÂN TÍCH TRANG BÌA (COVER PAGE) ===================")

for i in range(min(30, len(doc.paragraphs))):
    p = doc.paragraphs[i]
    text = p.text
    align = str(p.alignment)
    style = p.style.name if p.style else "Normal"
    
    font_names = []
    font_sizes = []
    bolds = []
    italics = []
    
    for r in p.runs:
        font_names.append(r.font.name or "Inherited")
        font_sizes.append(r.font.size.pt if r.font.size else "Inherited")
        bolds.append(r.bold)
        italics.append(r.italic)
        
    sb = p.paragraph_format.space_before.pt if p.paragraph_format.space_before else 0
    sa = p.paragraph_format.space_after.pt if p.paragraph_format.space_after else 0
    ls = p.paragraph_format.line_spacing
    
    lines.append(f"P{i+1} [{style}] Align: {align} | SB: {sb}pt | SA: {sa}pt | LS: {ls}")
    lines.append(f"   Text: '{text}'")
    lines.append(f"   Fonts: {font_names} | Sizes: {font_sizes} | Bold: {bolds} | Italic: {italics}")
    lines.append("-" * 60)

lines.append("\n=================== 2. PHÂN TÍCH MỤC LỤC & DANH MỤC ===================")
for i in range(30, min(100, len(doc.paragraphs))):
    p = doc.paragraphs[i]
    text = p.text
    if not text.strip():
        continue
    align = str(p.alignment)
    style = p.style.name if p.style else "Normal"
    
    font_names = set(r.font.name or "Inherited" for r in p.runs)
    font_sizes = set(r.font.size.pt if r.font.size else "Inherited" for r in p.runs)
    bolds = set(r.bold for r in p.runs)
    
    lines.append(f"P{i+1} [{style}] Align: {align} | Text: '{text}' | Font: {font_names} | Size: {font_sizes} | Bold: {bolds}")

# Check borders on Section 1 / Cover page
lines.append("\n=================== 3. SHAPES / BORDERS / IMAGES ON COVER ===================")
inline_shapes = doc.inline_shapes
lines.append(f"Total inline shapes: {len(inline_shapes)}")
for idx, shape in enumerate(inline_shapes):
    lines.append(f"Shape {idx+1}: Type={shape.type}, Width={shape.width}, Height={shape.height}")

with open("cover_and_toc_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Saved cover_and_toc_analysis.txt!")
