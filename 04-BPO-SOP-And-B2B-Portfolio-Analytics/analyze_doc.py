import docx
from docx.shared import Inches, Pt, Cm, RGBColor
import json
import os

doc = docx.Document("BÀI MẪU.docx")

analysis = {
    "sections": [],
    "styles_used": set(),
    "fonts_used": set(),
    "font_sizes_used": set(),
    "line_spacings": set(),
    "space_befores": set(),
    "space_afters": set(),
    "headings": [],
    "tables_count": len(doc.tables),
    "paragraphs_count": len(doc.paragraphs),
    "full_outline": [],
    "sample_paragraphs": []
}

for i, s in enumerate(doc.sections):
    sec_info = {
        "section": i + 1,
        "page_width_cm": round(s.page_width.cm, 2) if s.page_width else None,
        "page_height_cm": round(s.page_height.cm, 2) if s.page_height else None,
        "top_margin_cm": round(s.top_margin.cm, 2) if s.top_margin else None,
        "bottom_margin_cm": round(s.bottom_margin.cm, 2) if s.bottom_margin else None,
        "left_margin_cm": round(s.left_margin.cm, 2) if s.left_margin else None,
        "right_margin_cm": round(s.right_margin.cm, 2) if s.right_margin else None,
        "header_distance_cm": round(s.header_distance.cm, 2) if s.header_distance else None,
        "footer_distance_cm": round(s.footer_distance.cm, 2) if s.footer_distance else None,
    }
    analysis["sections"].append(sec_info)

for p in doc.paragraphs:
    text = p.text.strip()
    if not text:
        continue
    
    style_name = p.style.name if p.style else "Normal"
    analysis["styles_used"].add(style_name)

    fonts = [r.font.name for r in p.runs if r.font.name]
    sizes = [r.font.size.pt for r in p.runs if r.font.size]
    bolds = [r.bold for r in p.runs if r.bold is not None]
    
    for f in fonts:
        analysis["fonts_used"].add(f)
    for sz in sizes:
        analysis["font_sizes_used"].add(sz)
        
    ls = p.paragraph_format.line_spacing
    sb = p.paragraph_format.space_before
    sa = p.paragraph_format.space_after
    
    if ls is not None:
        analysis["line_spacings"].add(str(ls))
    if sb is not None:
        analysis["space_befores"].add(str(sb))
    if sa is not None:
        analysis["space_afters"].add(str(sa))

    # Detect headings or main structural lines
    is_heading = style_name.startswith("Heading") or (len(text) < 120 and (text.isupper() or any(text.startswith(prefix) for prefix in ["CHƯƠNG", "Chương", "PHẦN", "Phần", "BÀI", "Bài", "TRƯỜNG", "BÁO CÁO", "DANH MỤC", "MỤC LỤC", "LỜI CẢM ƠN", "KẾT LUẬN"])))
    
    if is_heading:
        analysis["headings"].append({
            "style": style_name,
            "text": text,
            "fonts": fonts,
            "sizes": sizes,
            "bold": any(bolds),
            "align": str(p.alignment)
        })

    analysis["full_outline"].append({
        "style": style_name,
        "text": text[:120],
        "is_heading": is_heading,
        "fonts": list(set(fonts)),
        "sizes": list(set(sizes)),
        "align": str(p.alignment)
    })

# Convert sets to lists for output
analysis["styles_used"] = list(analysis["styles_used"])
analysis["fonts_used"] = list(analysis["fonts_used"])
analysis["font_sizes_used"] = list(analysis["font_sizes_used"])
analysis["line_spacings"] = list(analysis["line_spacings"])
analysis["space_befores"] = list(analysis["space_befores"])
analysis["space_afters"] = list(analysis["space_afters"])

with open("analysis_results.json", "w", encoding="utf-8") as f:
    json.dump(analysis, f, ensure_ascii=False, indent=2)

print("Saved analysis_results.json successfully!")
