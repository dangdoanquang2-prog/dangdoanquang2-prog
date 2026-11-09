import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

import slides_data_model

# ---------------------------------------------------------------------------
# MCKINSEY / BCG CLEAN EXECUTIVE LIGHT COLOR PALETTE
# ---------------------------------------------------------------------------
BG_CANVAS = RGBColor(248, 250, 252)     # #F8FAFC - Soft Executive Slate Off-White
CARD_WHITE = RGBColor(255, 255, 255)    # #FFFFFF - Pure White Card Fill
CARD_BORDER = RGBColor(226, 232, 240)   # #E2E8F0 - Crisp Slate 200 Border
CARD_MUTED = RGBColor(241, 245, 249)    # #F1F5F9 - Slate 100 Light Container

NAVY_DARK = RGBColor(15, 23, 42)        # #0F172A - Primary Text & Main Headings
NAVY_HEADER = RGBColor(20, 35, 75)      # #14234B - Table Header Navy
NAVY_ACCENT = RGBColor(30, 58, 138)     # #1E3A8A - Corporate Brand Navy

BLUE_ROYAL = RGBColor(37, 99, 235)      # #2563EB - Royal Blue Accent
BLUE_LIGHT = RGBColor(239, 246, 255)    # #EFF6FF - Soft Blue Tint Pill
BLUE_BORDER = RGBColor(191, 219, 254)   # #BFDBFE - Soft Blue Border

GREEN_EMERALD = RGBColor(5, 150, 105)   # #059669 - Emerald Green Accent (Winner KH A)
GREEN_LIGHT = RGBColor(236, 253, 245)   # #ECFDF5 - Soft Green Tint Pill
GREEN_BORDER = RGBColor(167, 243, 208)  # #A7F3D0 - Soft Green Border

CYAN_SKY = RGBColor(2, 132, 199)        # #0284C7 - Sky Blue Accent (KH D)
CYAN_LIGHT = RGBColor(240, 249, 255)    # #F0F9FF - Soft Sky Tint Pill
CYAN_BORDER = RGBColor(186, 230, 253)   # #BAE6FD - Soft Sky Border

AMBER_GOLD = RGBColor(217, 119, 6)      # #D97706 - Amber Accent (KH B)
AMBER_LIGHT = RGBColor(255, 251, 235)   # #FFFBEB - Soft Amber Tint Pill
AMBER_BORDER = RGBColor(253, 230, 138)  # #FDE68A - Soft Amber Border

RED_ROSE = RGBColor(220, 38, 38)        # #DC2626 - Coral Red Accent (KH C)
RED_LIGHT = RGBColor(254, 242, 242)     # #FEF2F2 - Soft Red Tint Pill
RED_BORDER = RGBColor(254, 202, 202)    # #FECACA - Soft Red Border

PURPLE = RGBColor(124, 58, 237)         # #7C3AED - Strategic Purple
PURPLE_LIGHT = RGBColor(245, 243, 255)  # #F5F3FF - Soft Purple Tint Pill
PURPLE_BORDER = RGBColor(221, 214, 254) # #DDD6FE - Soft Purple Border

TEXT_HEAD = RGBColor(15, 23, 42)        # #0F172A - Slate 900
TEXT_BODY = RGBColor(51, 65, 85)        # #334155 - Slate 700
TEXT_MUTED = RGBColor(100, 116, 139)    # #64748B - Slate 500
TEXT_DIM = RGBColor(148, 163, 184)      # #94A3B8 - Slate 400
TEXT_WHITE = RGBColor(255, 255, 255)

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return RGBColor(*(int(hex_str[i:i+2], 16) for i in (0, 2, 4)))

def set_slide_background(slide):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = BG_CANVAS

def create_header(slide, tag, action_title, subtitle, slide_num, total=20):
    # Tag Pill (Crisp Navy with White Text)
    tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(2.6), Inches(0.3))
    tag_box.fill.solid()
    tag_box.fill.fore_color.rgb = NAVY_DARK
    tag_box.line.color.rgb = NAVY_DARK
    tf = tag_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = tag.upper()
    p.font.name = "Arial"
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.alignment = PP_ALIGN.CENTER

    # Action Title (Deep Slate Navy)
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.74), Inches(11.7), Inches(0.55))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = action_title
    p.font.name = "Arial"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK

    # Subtitle / So-What Context
    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.32), Inches(11.7), Inches(0.35))
        tf = sub_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = subtitle
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED

    # Bottom Separator Line
    sep = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.015))
    sep.fill.solid()
    sep.fill.fore_color.rgb = CARD_BORDER
    sep.line.fill.background()

    # Footer Left
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.06), Inches(8.5), Inches(0.3))
    tf = footer_box.text_frame
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = "U&I LOGISTICS CORPORATION  |  BÁO CÁO THẨM ĐỊNH & SÀNG LỌC KHÁCH HÀNG B2B (CLIENT QUALIFICATION)"
    p.font.name = "Arial"
    p.font.size = Pt(8)
    p.font.color.rgb = TEXT_DIM

    # Footer Right Slide Number
    num_box = slide.shapes.add_textbox(Inches(10.5), Inches(7.06), Inches(2.0), Inches(0.3))
    tf = num_box.text_frame
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = f"SLIDE {slide_num:02d} / {total:02d}"
    p.font.name = "Arial"
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = BLUE_ROYAL
    p.alignment = PP_ALIGN.RIGHT

def attach_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

def add_card_with_stripe(slide, left, top, width, height, stripe_color, bg_color=CARD_WHITE, border_color=CARD_BORDER):
    # Base card with sharp modern consulting corners
    card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)

    # Perfectly aligned top accent stripe
    stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.07))
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = stripe_color
    stripe.line.fill.background()
    return card

# ---------------------------------------------------------------------------
# SLIDE BUILDERS (EXECUTIVE MCKINSEY / BCG LIGHT THEME)
# ---------------------------------------------------------------------------

def build_slide_1(prs, data):
    # Slide 1: Hero Cover Slide
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)

    # Top Tag (ONLY ONE! No duplicates)
    tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.7), Inches(3.6), Inches(0.35))
    tag_box.fill.solid()
    tag_box.fill.fore_color.rgb = NAVY_DARK
    tag_box.line.color.rgb = NAVY_DARK
    p = tag_box.text_frame.paragraphs[0]
    p.text = data["tag"].upper() + "  |  BÁO CÁO ĐỀ ÁN"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.alignment = PP_ALIGN.CENTER

    # Hero Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(1.4))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = data["action_title"]
    p.font.name = "Arial"
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK

    # Subtitle
    sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.6), Inches(11.7), Inches(0.6))
    tf = sub_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = data["subtitle"]
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    # Benchmark Card
    bm_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.35), Inches(11.7), Inches(0.85))
    bm_card.fill.solid()
    bm_card.fill.fore_color.rgb = CARD_WHITE
    bm_card.line.color.rgb = BLUE_BORDER
    bm_card.line.width = Pt(1.5)

    # Left stripe for benchmark
    stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.35), Inches(0.1), Inches(0.85))
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = BLUE_ROYAL
    stripe.line.fill.background()

    tf = bm_card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    p = tf.paragraphs[0]
    p.text = "★ HỆ QUY CHIẾU THỰC NGHIỆM: " + data["benchmark"].split(": ")[-1].upper()
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = BLUE_ROYAL

    p2 = tf.add_paragraph()
    p2.text = "Doanh thu năm 2025: 1.163,52 tỷ VNĐ  •  Biên lợi nhuận ròng: 5,43%  •  Tôn chỉ: 'Clients' Interests First'"
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_BODY

    # 4 Executive KPI Hero Cards
    kpis = data.get("kpis", [])
    card_w = Inches(2.78)
    spacing = Inches(0.18)
    colors = [GREEN_EMERALD, BLUE_ROYAL, PURPLE, GREEN_EMERALD]
    subtexts = [
        "Cụm kho lớn nhất ĐNÁ\nKiểm soát ẩm tự động <63%",
        "Tuyến viễn dương US\nChiếm 55% sản lượng U&I",
        "Biên lợi nhuận ròng 5,43%\nBảo toàn vốn lưu động",
        "Tương thích 100% kho gỗ\nKhai thác trọn vẹn chuỗi 3PL"
    ]

    for i, kpi in enumerate(kpis):
        left = Inches(0.8) + i * (card_w + spacing)
        col = colors[i]
        card = add_card_with_stripe(slide, left, Inches(4.5), card_w, Inches(2.2), col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.12)
        tf.margin_top = Inches(0.2)

        p1 = tf.paragraphs[0]
        p1.text = kpi["val"]
        p1.font.size = Pt(22)
        p1.font.bold = True
        p1.font.color.rgb = col
        p1.alignment = PP_ALIGN.CENTER

        p2 = tf.add_paragraph()
        p2.text = kpi["lbl"]
        p2.font.size = Pt(10.5)
        p2.font.bold = True
        p2.font.color.rgb = NAVY_DARK
        p2.alignment = PP_ALIGN.CENTER

        p3 = tf.add_paragraph()
        p3.text = subtexts[i]
        p3.font.size = Pt(8.5)
        p3.font.color.rgb = TEXT_MUTED
        p3.alignment = PP_ALIGN.CENTER

    # Bottom Separator & Footer
    sep = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.015))
    sep.fill.solid()
    sep.fill.fore_color.rgb = CARD_BORDER
    sep.line.fill.background()

    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.06), Inches(8.5), Inches(0.3))
    tf = footer_box.text_frame
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = "U&I LOGISTICS CORPORATION  |  BÁO CÁO THẨM ĐỊNH & SÀNG LỌC KHÁCH HÀNG B2B (CLIENT QUALIFICATION)"
    p.font.name = "Arial"
    p.font.size = Pt(8)
    p.font.color.rgb = TEXT_DIM

    num_box = slide.shapes.add_textbox(Inches(10.5), Inches(7.06), Inches(2.0), Inches(0.3))
    tf = num_box.text_frame
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = "SLIDE 01 / 20"
    p.font.name = "Arial"
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = BLUE_ROYAL
    p.alignment = PP_ALIGN.RIGHT

    attach_speaker_notes(slide, data["notes"])

def build_slide_2(prs, data):
    # Slide 2: SCQA & Agenda
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 2)

    # Left: SCQA (Width 6.4 in)
    scqa_w = Inches(6.3)
    scqa = data["scqa"]
    items = [
        ("SITUATION (Bối cảnh U&I)", scqa["s"], BLUE_ROYAL, BLUE_LIGHT),
        ("COMPLICATION (Thách thức phân hóa)", scqa["c"], AMBER_GOLD, AMBER_LIGHT),
        ("QUESTION (Câu hỏi chiến lược)", scqa["q"], PURPLE, PURPLE_LIGHT),
        ("ANSWER (Giải pháp WSM)", scqa["a"], GREEN_EMERALD, GREEN_LIGHT)
    ]
    card_h = Inches(1.18)
    for i, (title, content, col, tint) in enumerate(items):
        top = Inches(1.8) + i * Inches(1.28)
        card = add_card_with_stripe(slide, Inches(0.8), top, scqa_w, card_h, col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.12)
        tf.margin_left = tf.margin_right = Inches(0.18)

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = col

        p2 = tf.add_paragraph()
        body = content.split("): ")[-1] if "): " in content else content
        p2.text = body
        p2.font.size = Pt(9)
        p2.font.color.rgb = TEXT_BODY

    # Right: 4 Agenda Cards (Width 5.2 in)
    agenda_w = Inches(5.2)
    top_agenda = Inches(1.8)

    title_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.3), top_agenda, agenda_w, Inches(0.45))
    title_card.fill.solid()
    title_card.fill.fore_color.rgb = NAVY_DARK
    title_card.line.color.rgb = NAVY_DARK
    p = title_card.text_frame.paragraphs[0]
    p.text = "4 TRỌNG TÂM CHIẾN LƯỢC CỦA ĐỀ ÁN"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.alignment = PP_ALIGN.CENTER

    agenda_items = data.get("agenda", [])
    for j, item in enumerate(agenda_items):
        top = top_agenda + Inches(0.58) + j * Inches(1.12)
        card = add_card_with_stripe(slide, Inches(7.3), top, agenda_w, Inches(1.02), BLUE_ROYAL)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.18)
        tf.margin_top = Inches(0.15)

        p = tf.paragraphs[0]
        p.text = f"MỤC TIÊU 0{j+1}"
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = BLUE_ROYAL

        p2 = tf.add_paragraph()
        p2.text = item
        p2.font.size = Pt(10.5)
        p2.font.bold = True
        p2.font.color.rgb = NAVY_DARK

    attach_speaker_notes(slide, data["notes"])

def build_slide_3(prs, data):
    # Slide 3: 4 Clients Profiles
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 3)

    clients = data.get("clients", [])
    w = Inches(2.78)
    spacing = Inches(0.18)
    colors = [GREEN_EMERALD, CYAN_SKY, AMBER_GOLD, RED_ROSE]
    badge_tints = [GREEN_LIGHT, CYAN_LIGHT, AMBER_LIGHT, RED_LIGHT]
    badge_borders = [GREEN_BORDER, CYAN_BORDER, AMBER_BORDER, RED_BORDER]

    for i, c in enumerate(clients):
        left = Inches(0.8) + i * (w + spacing)
        col = colors[i]
        card = add_card_with_stripe(slide, left, Inches(1.8), w, Inches(5.0), col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.14)
        tf.margin_top = Inches(0.18)

        # Header Pill
        p = tf.paragraphs[0]
        p.text = f"KHÁCH HÀNG {c['id']}"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        p.alignment = PP_ALIGN.CENTER

        p_badge = tf.add_paragraph()
        p_badge.text = f"[{c['badge'].upper()}]"
        p_badge.font.size = Pt(9.5)
        p_badge.font.bold = True
        p_badge.font.color.rgb = col
        p_badge.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        p_name = tf.add_paragraph()
        p_name.text = f"• Ngành hàng: {c['name']}"
        p_name.font.size = Pt(9.5)
        p_name.font.bold = True
        p_name.font.color.rgb = NAVY_DARK

        p_vol = tf.add_paragraph()
        p_vol.text = f"• Sản lượng: {c['vol']}"
        p_vol.font.size = Pt(9)
        p_vol.font.color.rgb = TEXT_BODY

        p_route = tf.add_paragraph()
        p_route.text = f"• Tuyến đường: {c['route']}"
        p_route.font.size = Pt(9)
        p_route.font.color.rgb = TEXT_BODY

        tf.add_paragraph()

        p_issue_title = tf.add_paragraph()
        p_issue_title.text = "Vấn đề / Nhu cầu chính:"
        p_issue_title.font.size = Pt(9.5)
        p_issue_title.font.bold = True
        p_issue_title.font.color.rgb = col

        p_issue = tf.add_paragraph()
        p_issue.text = c['issue']
        p_issue.font.size = Pt(9)
        p_issue.font.color.rgb = TEXT_BODY

        tf.add_paragraph()

        p_rec = tf.add_paragraph()
        rec_texts = [
            "Chiến lược: Tấn công toàn lực, ký HĐ năm, tích hợp EDI/WMS",
            "Chiến lược: Liên danh Lead Logistics, thầu phụ nâng hạ",
            "Chiến lược: Chỉ nhận cước/HQ, từ chối rủi ro chuỗi lạnh",
            "Chiến lược: Từ chối văn bản 24h, loại bỏ đơn hàng âm biên"
        ]
        p_rec.text = rec_texts[i]
        p_rec.font.size = Pt(8.5)
        p_rec.font.bold = True
        p_rec.font.color.rgb = NAVY_DARK

    attach_speaker_notes(slide, data["notes"])

def build_slide_4(prs, data):
    # Slide 4: 4 Pillars of U&I Capabilities
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 4)

    pillars = data.get("pillars", [])
    w = Inches(2.78)
    spacing = Inches(0.18)
    colors = [BLUE_ROYAL, GREEN_EMERALD, PURPLE, AMBER_GOLD]

    for i, p in enumerate(pillars):
        left = Inches(0.8) + i * (w + spacing)
        col = colors[i]
        card = add_card_with_stripe(slide, left, Inches(1.8), w, Inches(5.0), col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.14)
        tf.margin_top = Inches(0.18)

        p_title = tf.paragraphs[0]
        p_title.text = p["title"]
        p_title.font.size = Pt(11)
        p_title.font.bold = True
        p_title.font.color.rgb = col
        p_title.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        for spec in p["specs"]:
            p_spec = tf.add_paragraph()
            p_spec.text = f"• {spec}"
            p_spec.font.size = Pt(9)
            p_spec.font.color.rgb = TEXT_BODY

    attach_speaker_notes(slide, data["notes"])

def build_slide_5(prs, data):
    # Slide 5: Core Strengths vs Limitations Table
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 5)

    rows_data = data.get("table", [])
    rows_count = len(rows_data) + 1
    cols_count = 4

    table_shape = slide.shapes.add_table(rows_count, cols_count, Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    table = table_shape.table
    table.columns[0].width = Inches(1.8)
    table.columns[1].width = Inches(3.9)
    table.columns[2].width = Inches(3.8)
    table.columns[3].width = Inches(2.2)

    headers = ["Lĩnh vực / Khía cạnh", "Thế mạnh cốt lõi U&I", "Ranh giới / Giới hạn vận hành", "Đánh giá tương thích"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_HEADER
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

    for i, r in enumerate(rows_data):
        row_idx = i + 1
        vals = [r["col1"], r["col2"], r["col3"], r["fit"]]
        for j, val in enumerate(vals):
            cell = table.cell(row_idx, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_WHITE if row_idx % 2 == 1 else CARD_MUTED
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(9)
            if j == 0:
                p.font.bold = True
                p.font.color.rgb = NAVY_DARK
            elif j == 1:
                p.font.color.rgb = GREEN_EMERALD
            elif j == 2:
                p.font.color.rgb = RED_ROSE if "KHÔNG" in val else TEXT_BODY
            elif j == 3:
                p.font.bold = True
                p.font.color.rgb = GREEN_EMERALD if "KH A" in val else (AMBER_GOLD if "D" in val else RED_ROSE)

    attach_speaker_notes(slide, data["notes"])

def build_slide_6(prs, data):
    # Slide 6: WSM Methodology (5 Criteria)
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 6)

    weights = data.get("weights", [])
    w = Inches(11.7)
    card_h = Inches(0.92)
    colors = [BLUE_ROYAL, GREEN_EMERALD, PURPLE, AMBER_GOLD, RED_ROSE]

    for i, wt in enumerate(weights):
        top = Inches(1.8) + i * Inches(1.02)
        col = colors[i]
        card = add_card_with_stripe(slide, Inches(0.8), top, w, card_h, col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_top = Inches(0.12)

        p1 = tf.paragraphs[0]
        p1.text = f"{wt['name']}   |   Trọng số: {wt['pts']} ({wt['pct']})"
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = wt["reason"]
        p2.font.size = Pt(9)
        p2.font.color.rgb = TEXT_BODY

    attach_speaker_notes(slide, data["notes"])

def build_slide_7(prs, data):
    # Slide 7: WSM Scorecard Table
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 7)

    rows_data = data.get("rows", [])
    rows_count = len(rows_data) + 1
    cols_count = 5

    table_shape = slide.shapes.add_table(rows_count, cols_count, Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    table = table_shape.table
    table.columns[0].width = Inches(3.7)
    table.columns[1].width = Inches(2.0)
    table.columns[2].width = Inches(2.0)
    table.columns[3].width = Inches(2.0)
    table.columns[4].width = Inches(2.0)

    headers = ["Tiêu chí đánh giá WSM (Trọng số)", "KH A (Furniture)", "KH D (Machinery)", "KH B (Fruit)", "KH C (E-com)"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_HEADER
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

    for i, r in enumerate(rows_data):
        row_idx = i + 1
        is_highlight = r.get("is_total", False) or r.get("is_rank", False) or r.get("is_dec", False)
        vals = [r["crit"], r["a"], r["d"], r["b"], r["c"]]
        for j, val in enumerate(vals):
            cell = table.cell(row_idx, j)
            cell.fill.solid()
            if is_highlight:
                cell.fill.fore_color.rgb = NAVY_DARK
            else:
                if j == 1:
                    cell.fill.fore_color.rgb = GREEN_LIGHT  # Highlight Winner KH A
                elif j == 4:
                    cell.fill.fore_color.rgb = RED_LIGHT    # Highlight Loser KH C
                else:
                    cell.fill.fore_color.rgb = CARD_WHITE if row_idx % 2 == 1 else CARD_MUTED
            
            p = cell.text_frame.paragraphs[0]
            p.text = str(val)
            p.font.size = Pt(9)
            if is_highlight:
                p.font.bold = True
                p.font.color.rgb = TEXT_WHITE
            else:
                if j == 0:
                    p.font.bold = True
                    p.font.color.rgb = NAVY_DARK
                elif j == 1:
                    p.font.bold = True
                    p.font.color.rgb = GREEN_EMERALD
                elif j == 2:
                    p.font.color.rgb = CYAN_SKY
                elif j == 3:
                    p.font.color.rgb = AMBER_GOLD
                elif j == 4:
                    p.font.color.rgb = RED_ROSE

    attach_speaker_notes(slide, data["notes"])

def build_slide_8(prs, data):
    # Slide 8: 2x2 Portfolio Matrix
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 8)

    # Matrix Axis Guidance Banner
    axis_banner = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.72), Inches(11.7), Inches(0.32))
    axis_banner.fill.solid()
    axis_banner.fill.fore_color.rgb = CARD_MUTED
    axis_banner.line.color.rgb = CARD_BORDER
    p_ax = axis_banner.text_frame.paragraphs[0]
    p_ax.text = "▲ TRỤC TUNG (Y): QUY MÔ & GIÁ TRỊ THƯƠNG MẠI  |  ► TRỤC HOÀNH (X): ĐỘ TƯƠNG THÍCH NĂNG LỰC CỐT LÕI"
    p_ax.font.size = Pt(9)
    p_ax.font.bold = True
    p_ax.font.color.rgb = NAVY_ACCENT
    p_ax.alignment = PP_ALIGN.CENTER

    cards = data.get("matrix_cards", [])
    positions = [
        (Inches(0.8), Inches(2.15)),  # top left (KH D)
        (Inches(6.8), Inches(2.15)),  # top right (KH A)
        (Inches(0.8), Inches(4.55)),  # bottom left (KH C)
        (Inches(6.8), Inches(4.55)),  # bottom right (KH B)
    ]
    colors = [CYAN_SKY, GREEN_EMERALD, RED_ROSE, AMBER_GOLD]
    kpis = [
        "Quy mô: 15 Tỷ VNĐ/năm • Biên GP: 15-18% • L/C an toàn",
        "Quy mô: 102 Tỷ VNĐ/năm • Biên GP: 20-25% • Khai thác 100% kho gỗ",
        "Quy mô: 5,4 Tỷ VNĐ/năm • Biên GP: ÂM (-10%) • Càng làm càng lỗ",
        "Quy mô: 1,65 Tỷ VNĐ/năm • Biên GP: < 8% • Rủi ro chuỗi lạnh cao"
    ]
    w = Inches(5.7)
    h = Inches(2.25)

    for i, c in enumerate(cards):
        left, top = positions[i]
        col = colors[i]
        card = add_card_with_stripe(slide, left, top, w, h, col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.18)
        tf.margin_top = Inches(0.15)

        p = tf.paragraphs[0]
        p.text = c["q"]
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = col

        p_t = tf.add_paragraph()
        p_t.text = c["target"]
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY_DARK

        p_pos = tf.add_paragraph()
        p_pos.text = "• Vị thế: " + c["pos"]
        p_pos.font.size = Pt(8.5)
        p_pos.font.color.rgb = TEXT_MUTED

        p_act = tf.add_paragraph()
        p_act.text = "• Chiến lược: " + c["action"]
        p_act.font.size = Pt(8.5)
        p_act.font.color.rgb = TEXT_BODY

        p_kpi = tf.add_paragraph()
        p_kpi.text = "★ " + kpis[i]
        p_kpi.font.size = Pt(8.5)
        p_kpi.font.bold = True
        p_kpi.font.color.rgb = col

    attach_speaker_notes(slide, data["notes"])

def build_slide_9(prs, data):
    # Slide 9: P&L Exhibit (4 Financial Cards)
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 9)

    fins = data.get("fin", [])
    w = Inches(2.78)
    spacing = Inches(0.18)
    colors = [GREEN_EMERALD, CYAN_SKY, AMBER_GOLD, RED_ROSE]

    for i, f in enumerate(fins):
        left = Inches(0.8) + i * (w + spacing)
        col = colors[i]
        card = add_card_with_stripe(slide, left, Inches(1.8), w, Inches(5.0), col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.14)
        tf.margin_top = Inches(0.18)

        p = tf.paragraphs[0]
        p.text = f["name"]
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        p_rev_lbl = tf.add_paragraph()
        p_rev_lbl.text = "DOANH THU NĂM DỰ KIẾN:"
        p_rev_lbl.font.size = Pt(8.5)
        p_rev_lbl.font.color.rgb = TEXT_MUTED
        p_rev_lbl.alignment = PP_ALIGN.CENTER

        p_rev = tf.add_paragraph()
        p_rev.text = f"{f['rev_vnd']}"
        p_rev.font.size = Pt(16)
        p_rev.font.bold = True
        p_rev.font.color.rgb = NAVY_DARK
        p_rev.alignment = PP_ALIGN.CENTER

        p_share = tf.add_paragraph()
        p_share.text = f"{f['rev_usd']} ({f['share']})"
        p_share.font.size = Pt(8.5)
        p_share.font.color.rgb = TEXT_MUTED
        p_share.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        p_margin = tf.add_paragraph()
        p_margin.text = f"BIÊN LỢI NHUẬN GỘP:\n{f['margin']}"
        p_margin.font.size = Pt(10)
        p_margin.font.bold = True
        p_margin.font.color.rgb = col
        p_margin.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        p_gp_lbl = tf.add_paragraph()
        p_gp_lbl.text = "LỢI NHUẬN GỘP ĐÓNG GÓP:"
        p_gp_lbl.font.size = Pt(8.5)
        p_gp_lbl.font.color.rgb = TEXT_MUTED
        p_gp_lbl.alignment = PP_ALIGN.CENTER

        p_gp = tf.add_paragraph()
        p_gp.text = f"{f['gp']}"
        p_gp.font.size = Pt(11)
        p_gp.font.bold = True
        p_gp.font.color.rgb = col
        p_gp.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        p_note = tf.add_paragraph()
        p_note.text = f"Đặc điểm vận hành: {f['note']}"
        p_note.font.size = Pt(8.5)
        p_note.font.color.rgb = TEXT_BODY

    attach_speaker_notes(slide, data["notes"])

def build_slide_10(prs, data):
    # Slide 10: Client A 3PL Integrated Process
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 10)

    steps = data.get("steps", [])
    w = Inches(2.78)
    spacing = Inches(0.18)

    for i, s in enumerate(steps):
        left = Inches(0.8) + i * (w + spacing)
        card = add_card_with_stripe(slide, left, Inches(1.8), w, Inches(5.0), GREEN_EMERALD)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.14)
        tf.margin_top = Inches(0.18)

        p_step = tf.paragraphs[0]
        p_step.text = f"BƯỚC {s['step']}"
        p_step.font.size = Pt(13)
        p_step.font.bold = True
        p_step.font.color.rgb = GREEN_EMERALD
        p_step.alignment = PP_ALIGN.CENTER

        p_title = tf.add_paragraph()
        p_title.text = s["title"]
        p_title.font.size = Pt(10.5)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY_DARK
        p_title.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        p_desc = tf.add_paragraph()
        p_desc.text = s["desc"]
        p_desc.font.size = Pt(9)
        p_desc.font.color.rgb = TEXT_BODY

    attach_speaker_notes(slide, data["notes"])

def build_slide_11(prs, data):
    # Slide 11: Client A Risk Defense (2 Big Cards)
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 11)

    risks = data.get("risks", [])
    w = Inches(5.7)
    colors = [RED_ROSE, AMBER_GOLD]

    for i, r in enumerate(risks):
        left = Inches(0.8) + i * Inches(6.0)
        col = colors[i]
        card = add_card_with_stripe(slide, left, Inches(1.8), w, Inches(5.0), col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.18)
        tf.margin_top = Inches(0.18)

        p = tf.paragraphs[0]
        p.text = r["title"]
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        tf.add_paragraph()

        p_prob_hdr = tf.add_paragraph()
        p_prob_hdr.text = "Bản chất rủi ro:"
        p_prob_hdr.font.size = Pt(10)
        p_prob_hdr.font.bold = True
        p_prob_hdr.font.color.rgb = NAVY_DARK

        p_prob = tf.add_paragraph()
        p_prob.text = r["problem"]
        p_prob.font.size = Pt(9)
        p_prob.font.color.rgb = TEXT_BODY

        tf.add_paragraph()

        p_sol_hdr = tf.add_paragraph()
        p_sol_hdr.text = "Cơ chế phòng ngừa & kiểm soát:"
        p_sol_hdr.font.size = Pt(10)
        p_sol_hdr.font.bold = True
        p_sol_hdr.font.color.rgb = GREEN_EMERALD

        for sol in r["solution"]:
            p_sol = tf.add_paragraph()
            p_sol.text = f"✔ {sol}"
            p_sol.font.size = Pt(9)
            p_sol.font.color.rgb = TEXT_BODY

    attach_speaker_notes(slide, data["notes"])

def build_slide_12(prs, data):
    # Slide 12: Client D Consortium Model (3 Cards)
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 12)

    parts = data.get("parts", [])
    w = Inches(3.75)
    spacing = Inches(0.22)
    colors = [BLUE_ROYAL, GREEN_EMERALD, AMBER_GOLD]

    for i, p in enumerate(parts):
        left = Inches(0.8) + i * (w + spacing)
        col = colors[i]
        card = add_card_with_stripe(slide, left, Inches(1.8), w, Inches(5.0), col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.16)
        tf.margin_top = Inches(0.18)

        p_title = tf.paragraphs[0]
        p_title.text = p["title"]
        p_title.font.size = Pt(11)
        p_title.font.bold = True
        p_title.font.color.rgb = col
        p_title.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        for item in p["items"]:
            p_item = tf.add_paragraph()
            p_item.text = item
            p_item.font.size = Pt(9)
            p_item.font.color.rgb = TEXT_BODY

    attach_speaker_notes(slide, data["notes"])

def build_slide_13(prs, data):
    # Slide 13: Client B Cold Chain Limits (3 Cards)
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 13)

    cards = data.get("cards", [])
    w = Inches(3.75)
    spacing = Inches(0.22)
    colors = [RED_ROSE, AMBER_GOLD, CYAN_SKY]

    for i, c in enumerate(cards):
        left = Inches(0.8) + i * (w + spacing)
        col = colors[i]
        card = add_card_with_stripe(slide, left, Inches(1.8), w, Inches(5.0), col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.16)
        tf.margin_top = Inches(0.18)

        p_title = tf.paragraphs[0]
        p_title.text = c["title"]
        p_title.font.size = Pt(10.5)
        p_title.font.bold = True
        p_title.font.color.rgb = col
        p_title.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        p_cont = tf.add_paragraph()
        p_cont.text = c["content"]
        p_cont.font.size = Pt(9)
        p_cont.font.color.rgb = TEXT_BODY

    attach_speaker_notes(slide, data["notes"])

def build_slide_14(prs, data):
    # Slide 14: Client C DNA Conflict & Unit Economics
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 14)

    # Left: DNA Conflict (Width 5.7 in)
    dna_items = data.get("left_dna", [])
    table_shape = slide.shapes.add_table(len(dna_items)+1, 4, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0))
    table = table_shape.table
    table.columns[0].width = Inches(1.7)
    table.columns[1].width = Inches(1.6)
    table.columns[2].width = Inches(1.6)
    table.columns[3].width = Inches(0.8)

    headers = ["Khía cạnh", "U&I Logistics", "KH C (TMĐT)", "Độ lệch"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_HEADER
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

    for i, d in enumerate(dna_items):
        row = i + 1
        vals = [d["crit"], d["ui"], d["c"], d["fit"]]
        for j, v in enumerate(vals):
            cell = table.cell(row, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_WHITE if row % 2 == 1 else CARD_MUTED
            p = cell.text_frame.paragraphs[0]
            p.text = v
            p.font.size = Pt(8.5)
            if j == 0:
                p.font.bold = True
                p.font.color.rgb = NAVY_DARK
            elif j == 3:
                p.font.bold = True
                p.font.color.rgb = RED_ROSE
            else:
                p.font.color.rgb = TEXT_BODY

    # Right: Unit Economics Waterfall (Width 5.7 in)
    pnl_items = data.get("right_pnl", [])
    table_shape2 = slide.shapes.add_table(len(pnl_items)+1, 2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
    table2 = table_shape2.table
    table2.columns[0].width = Inches(4.0)
    table2.columns[1].width = Inches(1.7)

    headers2 = ["Bóc tách Chi phí & Lợi nhuận / Đơn hàng", "Giá trị"]
    for j, h in enumerate(headers2):
        cell = table2.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_HEADER
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

    for i, pnl in enumerate(pnl_items):
        row = i + 1
        cell1 = table2.cell(row, 0)
        cell2 = table2.cell(row, 1)
        is_bold = pnl.get("bold", False)

        cell1.fill.solid()
        cell2.fill.solid()
        bg_col = RED_LIGHT if is_bold else (CARD_WHITE if row % 2 == 1 else CARD_MUTED)
        cell1.fill.fore_color.rgb = bg_col
        cell2.fill.fore_color.rgb = bg_col

        p1 = cell1.text_frame.paragraphs[0]
        p1.text = pnl["item"]
        p1.font.size = Pt(9)
        p1.font.bold = is_bold
        p1.font.color.rgb = RED_ROSE if is_bold else NAVY_DARK

        p2 = cell2.text_frame.paragraphs[0]
        p2.text = pnl["val"]
        p2.font.size = Pt(9.5)
        p2.font.bold = True
        p2.font.color.rgb = GREEN_EMERALD if "+ " in pnl["val"] else RED_ROSE
        p2.alignment = PP_ALIGN.RIGHT

    attach_speaker_notes(slide, data["notes"])

def build_slide_15(prs, data):
    # Slide 15: Risk Heatmap Table
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 15)

    headers = data.get("headers", [])
    matrix = data.get("matrix", [])

    table_shape = slide.shapes.add_table(len(matrix)+1, len(headers), Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    table = table_shape.table
    table.columns[0].width = Inches(2.5)
    table.columns[1].width = Inches(2.3)
    table.columns[2].width = Inches(2.3)
    table.columns[3].width = Inches(2.3)
    table.columns[4].width = Inches(2.3)

    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_HEADER
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

    for i, m in enumerate(matrix):
        row = i + 1
        cell0 = table.cell(row, 0)
        cell0.fill.solid()
        cell0.fill.fore_color.rgb = CARD_WHITE if row % 2 == 1 else CARD_MUTED
        p0 = cell0.text_frame.paragraphs[0]
        p0.text = m["name"]
        p0.font.size = Pt(9)
        p0.font.bold = True
        p0.font.color.rgb = NAVY_DARK

        client_keys = ["a", "d", "b", "c"]
        for j, k in enumerate(client_keys):
            cell = table.cell(row, j+1)
            risk_label, hex_c, desc = m[k]

            cell.fill.solid()
            if "THẤP" in risk_label:
                cell.fill.fore_color.rgb = GREEN_LIGHT
                col = GREEN_EMERALD
            elif "CAO" in risk_label:
                cell.fill.fore_color.rgb = RED_LIGHT
                col = RED_ROSE
            else:
                cell.fill.fore_color.rgb = AMBER_LIGHT
                col = AMBER_GOLD

            p1 = cell.text_frame.paragraphs[0]
            p1.text = f"[{risk_label}]"
            p1.font.size = Pt(9)
            p1.font.bold = True
            p1.font.color.rgb = col

            p2 = cell.text_frame.add_paragraph()
            p2.text = desc
            p2.font.size = Pt(8)
            p2.font.color.rgb = TEXT_BODY

    attach_speaker_notes(slide, data["notes"])

def build_slide_16(prs, data):
    # Slide 16: Porter's Bargaining Power (4 Cards)
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 16)

    cards = data.get("cards", [])
    w = Inches(2.78)
    spacing = Inches(0.18)
    colors = [GREEN_EMERALD, CYAN_SKY, AMBER_GOLD, RED_ROSE]

    for i, c in enumerate(cards):
        left = Inches(0.8) + i * (w + spacing)
        col = colors[i]
        card = add_card_with_stripe(slide, left, Inches(1.8), w, Inches(5.0), col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.14)
        tf.margin_top = Inches(0.18)

        p = tf.paragraphs[0]
        p.text = c["title"]
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = NAVY_DARK
        p.alignment = PP_ALIGN.CENTER

        p_status = tf.add_paragraph()
        p_status.text = c["status"]
        p_status.font.size = Pt(9)
        p_status.font.bold = True
        p_status.font.color.rgb = col
        p_status.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        for pt in c["points"]:
            p_pt = tf.add_paragraph()
            p_pt.text = f"• {pt}"
            p_pt.font.size = Pt(8.5)
            p_pt.font.color.rgb = TEXT_BODY

    attach_speaker_notes(slide, data["notes"])

def build_slide_17(prs, data):
    # Slide 17: SLA Framework (4 Tiers)
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 17)

    tiers = data.get("tiers", [])
    w = Inches(2.78)
    spacing = Inches(0.18)
    colors = [GREEN_EMERALD, CYAN_SKY, AMBER_GOLD, RED_ROSE]

    for i, t in enumerate(tiers):
        left = Inches(0.8) + i * (w + spacing)
        col = colors[i]
        card = add_card_with_stripe(slide, left, Inches(1.8), w, Inches(5.0), col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.14)
        tf.margin_top = Inches(0.18)

        p = tf.paragraphs[0]
        p.text = t["tier"]
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = col
        p.alignment = PP_ALIGN.CENTER

        p_sub = tf.add_paragraph()
        p_sub.text = f"[{t['type']}]"
        p_sub.font.size = Pt(9)
        p_sub.font.bold = True
        p_sub.font.color.rgb = NAVY_DARK
        p_sub.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        for term in t["terms"]:
            p_term = tf.add_paragraph()
            p_term.text = f"• {term}"
            p_term.font.size = Pt(8.5)
            p_term.font.color.rgb = TEXT_BODY

    attach_speaker_notes(slide, data["notes"])

def build_slide_18(prs, data):
    # Slide 18: 30-60-90 Days Roadmap
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 18)

    phases = data.get("phases", [])
    w = Inches(3.75)
    spacing = Inches(0.22)
    colors = [BLUE_ROYAL, PURPLE, GREEN_EMERALD]

    for i, ph in enumerate(phases):
        left = Inches(0.8) + i * (w + spacing)
        col = colors[i]
        card = add_card_with_stripe(slide, left, Inches(1.8), w, Inches(5.0), col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.16)
        tf.margin_top = Inches(0.18)

        p = tf.paragraphs[0]
        p.text = ph["phase"]
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col
        p.alignment = PP_ALIGN.CENTER

        p_t = tf.add_paragraph()
        p_t.text = ph["title"]
        p_t.font.size = Pt(10)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY_DARK
        p_t.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        for task in ph["tasks"]:
            p_task = tf.add_paragraph()
            p_task.text = f"✔ {task}"
            p_task.font.size = Pt(9)
            p_task.font.color.rgb = TEXT_BODY

    attach_speaker_notes(slide, data["notes"])

def build_slide_19(prs, data):
    # Slide 19: 4 Management Lessons
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 19)

    lessons = data.get("lessons", [])
    w = Inches(2.78)
    spacing = Inches(0.18)
    colors = [BLUE_ROYAL, GREEN_EMERALD, PURPLE, RED_ROSE]

    for i, l in enumerate(lessons):
        left = Inches(0.8) + i * (w + spacing)
        col = colors[i]
        card = add_card_with_stripe(slide, left, Inches(1.8), w, Inches(5.0), col)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.14)
        tf.margin_top = Inches(0.18)

        p_num = tf.paragraphs[0]
        p_num.text = f"NGUYÊN TẮC {l['num']}"
        p_num.font.size = Pt(12)
        p_num.font.bold = True
        p_num.font.color.rgb = col
        p_num.alignment = PP_ALIGN.CENTER

        p_title = tf.add_paragraph()
        p_title.text = l["title"]
        p_title.font.size = Pt(10)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY_DARK
        p_title.alignment = PP_ALIGN.CENTER

        tf.add_paragraph()

        p_desc = tf.add_paragraph()
        p_desc.text = l["desc"]
        p_desc.font.size = Pt(9)
        p_desc.font.color.rgb = TEXT_BODY

    attach_speaker_notes(slide, data["notes"])

def build_slide_20(prs, data):
    # Slide 20: Conclusion & Q&A
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    create_header(slide, data["tag"], data["action_title"], data["subtitle"], 20)

    # Left: Summary Bullets (Width 6.4 in)
    bullets = data.get("summary_bullets", [])
    card = add_card_with_stripe(slide, Inches(0.8), Inches(1.8), Inches(6.3), Inches(5.0), BLUE_ROYAL)
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)

    p = tf.paragraphs[0]
    p.text = "TỔNG KẾT BÀN GIAO ĐỀ ÁN CHIẾN LƯỢC"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BLUE_ROYAL

    tf.add_paragraph()

    for b in bullets:
        p_b = tf.add_paragraph()
        p_b.text = f"★ {b}"
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = TEXT_BODY

    # Right: Q&A Invitation Card (Width 5.1 in)
    qa_card = add_card_with_stripe(slide, Inches(7.4), Inches(1.8), Inches(5.1), Inches(5.0), GREEN_EMERALD)
    tf2 = qa_card.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_right = Inches(0.2)
    tf2.margin_top = Inches(0.4)

    p_qa = tf2.paragraphs[0]
    p_qa.text = "PHIÊN HỎI & ĐÁP\n(Q & A)"
    p_qa.font.size = Pt(24)
    p_qa.font.bold = True
    p_qa.font.color.rgb = GREEN_EMERALD
    p_qa.alignment = PP_ALIGN.CENTER

    tf2.add_paragraph()
    tf2.add_paragraph()

    p_credo = tf2.add_paragraph()
    p_credo.text = 'Tôn chỉ U&I Logistics:\n"CLIENTS\' INTERESTS FIRST"'
    p_credo.font.size = Pt(12)
    p_credo.font.bold = True
    p_credo.font.color.rgb = NAVY_DARK
    p_credo.alignment = PP_ALIGN.CENTER

    tf2.add_paragraph()

    p_inv = tf2.add_paragraph()
    p_inv.text = "Rất mong nhận được các câu hỏi phản biện, nhận xét và đánh giá từ Quý Thầy/Cô và Hội đồng!"
    p_inv.font.size = Pt(10.5)
    p_inv.font.color.rgb = TEXT_BODY
    p_inv.alignment = PP_ALIGN.CENTER

    attach_speaker_notes(slide, data["notes"])

# ---------------------------------------------------------------------------
# MAIN DISPATCHER
# ---------------------------------------------------------------------------
def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slides_list = slides_data_model.slides
    builders = {
        1: build_slide_1,
        2: build_slide_2,
        3: build_slide_3,
        4: build_slide_4,
        5: build_slide_5,
        6: build_slide_6,
        7: build_slide_7,
        8: build_slide_8,
        9: build_slide_9,
        10: build_slide_10,
        11: build_slide_11,
        12: build_slide_12,
        13: build_slide_13,
        14: build_slide_14,
        15: build_slide_15,
        16: build_slide_16,
        17: build_slide_17,
        18: build_slide_18,
        19: build_slide_19,
        20: build_slide_20,
    }

    print(f"Building {len(slides_list)} Clean Executive McKinsey-style PowerPoint slides...")
    for item in slides_list:
        slide_id = item["id"]
        builder = builders.get(slide_id)
        if builder:
            builder(prs, item)
            print(f"  Slide {slide_id:02d}: {item['action_title'][:45]}... Done")
        else:
            print(f"  Slide {slide_id:02d}: No builder found!")

    # Output to McKinsey Light presentation
    output_path = r"d:\hkdn\SLIDE_THUYET_TRINH_SANG_LOC_KHACH_HANG_MCKINSEY.pptx"
    prs.save(output_path)
    print(f"\nSuccessfully generated McKinsey Executive presentation at:\n  {output_path}")
    print(f"File size: {os.path.getsize(output_path)} bytes")

    # Also try to save to EDITABLE if unlocked, or provide alternative
    try:
        editable_path = r"d:\hkdn\SLIDE_THUYET_TRINH_SANG_LOC_KHACH_HANG_EDITABLE_NEW.pptx"
        prs.save(editable_path)
        print(f"Also saved backup to:\n  {editable_path}")
    except Exception as e:
        print(f"Could not save backup: {e}")

if __name__ == "__main__":
    main()
