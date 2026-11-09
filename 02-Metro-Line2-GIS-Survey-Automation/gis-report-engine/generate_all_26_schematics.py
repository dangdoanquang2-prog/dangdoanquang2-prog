import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

ALL_STATIONS = [
    ("ST01", "Phan Văn Hớn"),
    ("ST02", "Đông Hưng Thuận"),
    ("ST03", "An Sương"),
    ("ST04", "Nguyễn Ảnh Thủ"),
    ("ST05", "Nguyễn Thị Sóc"),
    ("ST06", "Bà Triệu"),
    ("ST07", "Lý Thường Kiệt"),
    ("ST08", "Nguyễn Thị Nuôi"),
    ("ST09", "Vòng cung Tây Bắc 2"),
    ("ST10", "Vành Đai 3"),
    ("ST11", "An Hạ"),
    ("ST12", "Tân Phú Trung"),
    ("ST13", "Hương Lộ 2"),
    ("ST14", "Đào Thị Kiểm"),
    ("ST15", "Lê Minh Nhựt"),
    ("ST16", "Tân Thông Hội"),
    ("ST17", "Trần Tử Bình"),
    ("ST18", "Huỳnh Văn Cọ"),
    ("ST19", "Củ Chi"),
    ("ST20", "BV Củ Chi"),
    ("ST21", "Nguyễn Thị Rành"),
    ("ST22", "Tân An Hội"),
    ("ST23", "Ba Sa"),
    ("ST24", "Phước Hiệp"),
    ("ST25", "Tỉnh Lộ 7"),
    ("ST26", "Thái Mỹ")
]

OUT_DIR = r"d:\baocaotudong\schematics_26"
os.makedirs(OUT_DIR, exist_ok=True)

def generate_schematic(active_code, out_path):
    fig, ax = plt.subplots(figsize=(11.5, 3.4), dpi=240)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    
    n_per_row = 13
    x_coords = [i * 1.0 for i in range(n_per_row)]
    
    # Tiêu đề dải tuyến
    ax.text(6.0, 3.25, "SƠ ĐỒ VỊ TRÍ NHÀ GA TRÊN HƯỚNG TUYẾN METRO TUYẾN 2 VÀ TUYẾN 2S",
            fontsize=10.5, fontweight='bold', color='#003366', ha='center', va='top', fontname='Times New Roman')
    
    # Dòng 1: Tuyến 2 (Tham Lương - An Hạ)
    ax.plot([-0.2, 12.2], [2.15, 2.15], color='#546e7a', linewidth=6.5, zorder=1, solid_capstyle='round')
    # Dòng 2: Tuyến 2S (An Hạ - Củ Chi)
    ax.plot([-0.2, 12.2], [0.85, 0.85], color='#546e7a', linewidth=6.5, zorder=1, solid_capstyle='round')
    
    # Nhãn phân đoạn
    ax.text(-0.5, 2.15, "TUYẾN 2\n(Tham Lương – An Hạ)", fontsize=7.5, fontweight='bold', color='#003366', ha='right', va='center', fontname='Times New Roman')
    ax.text(-0.5, 0.85, "TUYẾN 2S\n(An Hạ – Củ Chi)", fontsize=7.5, fontweight='bold', color='#003366', ha='right', va='center', fontname='Times New Roman')

    for idx, (code, name) in enumerate(ALL_STATIONS):
        row = 0 if idx < n_per_row else 1
        x = x_coords[idx % n_per_row]
        y = 2.15 if row == 0 else 0.85
        is_active = (code == active_code)
        
        if is_active:
            # Hào quang sáng đèn màu đỏ nổi bật
            circle_glow = patches.Circle((x, y), 0.24, facecolor='#ffcdd2', edgecolor='#e53935', linewidth=1.6, zorder=10)
            circle_core = patches.Circle((x, y), 0.15, facecolor='#d32f2f', edgecolor='#ffffff', linewidth=1.5, zorder=11)
            ax.add_patch(circle_glow)
            ax.add_patch(circle_core)
        else:
            circle_core = patches.Circle((x, y), 0.11, facecolor='#ffffff', edgecolor='#004b87', linewidth=1.2, zorder=5)
            circle_inner = patches.Circle((x, y), 0.05, facecolor='#90a4ae', edgecolor='none', zorder=6)
            ax.add_patch(circle_core)
            ax.add_patch(circle_inner)
            
        code_color = '#d32f2f' if is_active else '#e65100'
        ax.text(x, y + 0.26, code, fontsize=8.0 if is_active else 6.8, fontweight='bold',
                color=code_color, ha='center', va='bottom', fontname='Times New Roman')
        
        alt = (idx % 2 == 0)
        name_y = y - 0.24 if alt else y - 0.46
        name_color = '#b71c1c' if is_active else '#37474f'
        name_weight = 'bold' if is_active else 'normal'
        
        if not alt:
            ax.plot([x, x], [y - 0.12, y - 0.40], color='#cfd8dc', linewidth=0.7, zorder=2)
            
        display_name = name
        if len(name) > 9 and " " in name:
            words = name.split(" ")
            mid = len(words) // 2
            display_name = " ".join(words[:mid]) + "\n" + " ".join(words[mid:])
            
        ax.text(x, name_y, display_name, fontsize=7.0 if is_active else 6.2, fontweight=name_weight,
                color=name_color, ha='center', va='top', fontname='Times New Roman', linespacing=0.85)

    ax.set_xlim(-2.2, 13.0)
    ax.set_ylim(-0.35, 3.4)
    ax.axis('off')
    
    fig.savefig(out_path, bbox_inches='tight', dpi=240)
    plt.close(fig)

print("Starting generation of 26 station line schematics...")
for code, name in ALL_STATIONS:
    out_file = os.path.join(OUT_DIR, f"{code}_schematic.png")
    generate_schematic(code, out_file)
    print(f"Generated schematic for {code} - {name} -> {out_file}")

print("All 26 schematics successfully generated!")
