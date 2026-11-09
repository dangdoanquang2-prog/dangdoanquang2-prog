"""
Motorcycle Counter - Gradio Web Application
============================================
Beautiful web interface for uploading videos and counting
motorcycles with rider detection.
"""

import os
import sys

# Prepend local bin folder containing ffmpeg/ffprobe to PATH
bin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
if os.path.exists(bin_path):
    os.environ["PATH"] = bin_path + os.path.pathsep + os.environ["PATH"]

import cv2
import numpy as np
import tempfile
import threading
import queue
import gradio as gr
from motorcycle_counter import MotorcyclePersonCounter, format_summary, export_to_csv


# Ensure output directory exists
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_first_frame_into_editor(video_file):
    """Extract the first frame from the video and load it as background in gr.ImageEditor."""
    if video_file is None:
        return None
        
    if hasattr(video_file, "name"):
        video_path = video_file.name
    elif isinstance(video_file, dict) and "path" in video_file:
        video_path = video_file["path"]
    else:
        video_path = str(video_file)
        
    try:
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
    except Exception as e:
        print(f"DEBUG: Error extracting first frame: {str(e)}")
        return None
        
    if not ret or frame is None:
        return None
        
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return {"background": frame_rgb, "layers": [], "composite": frame_rgb}


def extract_line_coords_from_editor(editor_val):
    """
    Extract normalized coordinates [x1, y1, x2, y2] from the single largest continuous stroke
    in Gradio ImageEditor drawn layers to filter out any border noise or stray dots.
    """
    if editor_val is None or not isinstance(editor_val, dict):
        return None
        
    layers = editor_val.get("layers", [])
    if not layers:
        return None
        
    for layer in layers:
        if layer is None:
            continue
            
        h, w = layer.shape[:2]
        
        # Extract binary mask of drawn pixels
        if layer.shape[-1] == 4:
            mask = (layer[:, :, 3] > 10).astype(np.uint8) * 255
        else:
            gray = cv2.cvtColor(layer, cv2.COLOR_RGB2GRAY)
            _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
            
        # Find connected components to isolate the main drawn stroke
        num_labels, labels_im, stats, centroids = cv2.connectedComponentsWithStats(mask)
        if num_labels < 2:
            continue
            
        # Find the component with the largest area (excluding background label 0)
        max_idx = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        
        # Ignore tiny components/artifacts (under 20 pixels)
        if stats[max_idx, cv2.CC_STAT_AREA] < 20:
            continue
            
        # Extract points belonging only to the largest component
        pts = np.argwhere(labels_im == max_idx)
        
        if len(pts) < 5:
            continue
            
        # Coordinates in argwhere are [y, x]. Convert to [x, y]
        pts_xy = np.flip(pts, axis=1)
        
        # Convex hull to find extrema points
        hull = cv2.convexHull(pts_xy)
        hull_pts = hull.reshape(-1, 2)
        
        if len(hull_pts) < 2:
            continue
            
        # Find maximum distance pair
        max_dist = -1
        p1, p2 = hull_pts[0], hull_pts[-1]
        for i in range(len(hull_pts)):
            for j in range(i + 1, len(hull_pts)):
                d = np.linalg.norm(hull_pts[i] - hull_pts[j])
                if d > max_dist:
                    max_dist = d
                    p1, p2 = hull_pts[i], hull_pts[j]
                    
        # Normalize coordinates
        x1_norm = float(p1[0]) / w
        y1_norm = float(p1[1]) / h
        x2_norm = float(p2[0]) / w
        y2_norm = float(p2[1]) / h
        
        return [
            max(0.0, min(1.0, x1_norm)),
            max(0.0, min(1.0, y1_norm)),
            max(0.0, min(1.0, x2_norm)),
            max(0.0, min(1.0, y2_norm))
        ]
        
    return None


def process_video(
    video_file,
    model_size,
    conf_motorcycle,
    conf_person,
    nms_iou,
    line_position,
    use_custom_line,
    image_editor_val,
    count_mode,
    track_buffer,
    imgsz,
    progress=gr.Progress(),
):
    """Process uploaded video and yield real-time progress results."""
    if video_file is None:
        yield None, gr.update(visible=False), None, "⚠️ Vui lòng upload video trước!"
        return

    # Resolve actual file path string from Gradio file/dict/str object
    if hasattr(video_file, "name"):
        video_path = video_file.name
    elif isinstance(video_file, dict) and "path" in video_file:
        video_path = video_file["path"]
    else:
        video_path = str(video_file)

    # Output paths
    output_filename = "result_" + os.path.basename(video_path).rsplit(".", 1)[0] + ".mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    output_csv_filename = "report_" + os.path.basename(video_path).rsplit(".", 1)[0] + ".csv"
    output_csv_path = os.path.join(OUTPUT_DIR, output_csv_filename)

    # Queue for thread communication
    q = queue.Queue()

    def update_progress(current, total):
        q.put((current, total))

    try:
        progress(0, desc=f"Đang tải model {model_size}...")
        yield None, gr.update(visible=False), None, f"⏳ Đang tải model {model_size}..."

        # Setup line coords if custom line is enabled
        line_coords = None
        if use_custom_line and image_editor_val is not None:
            line_coords = extract_line_coords_from_editor(image_editor_val)
            if line_coords is not None:
                print(f"DEBUG: Using custom drawn line coordinates: {line_coords}")
            else:
                print("DEBUG: Custom line enabled but no drawings detected. Falling back to default line.")

        # Initialize counter
        counter = MotorcyclePersonCounter(
            model_size=model_size,
            conf_motorcycle=conf_motorcycle,
            conf_person=conf_person,
            iou_threshold=nms_iou,
            track_buffer=int(track_buffer),
            imgsz=int(imgsz),
        )

        # Container for background thread results
        thread_result = [None]

        def run_inference():
            try:
                summary = counter.process_video(
                    video_path=video_path,
                    output_path=output_path,
                    line_y_ratio=line_position,
                    count_mode=count_mode,
                    line_coords=line_coords,
                    progress_callback=update_progress,
                )
                thread_result[0] = summary
                q.put("DONE")
            except Exception as e:
                thread_result[0] = e
                q.put("ERROR")

        # Run in a background thread so we can yield progress to Gradio
        t = threading.Thread(target=run_inference)
        t.daemon = True
        t.start()

        # Listen for progress updates
        last_current = 0
        last_total = 0
        while t.is_alive() or not q.empty():
            try:
                msg = q.get(timeout=0.1)
                if msg == "DONE":
                    break
                elif msg == "ERROR":
                    raise thread_result[0]
                else:
                    current, total = msg
                    last_current = current
                    last_total = total
                    progress(current / total, desc=f"Đang xử lý frame {current}/{total}...")
                    yield gr.update(), gr.update(), gr.update(), f"⏳ Đang xử lý: Frame {current}/{total}..."
            except queue.Empty:
                continue

        t.join()

        # Handle errors from background thread
        if isinstance(thread_result[0], Exception):
            raise thread_result[0]

        summary = thread_result[0]
        if summary is None:
            raise RuntimeError("Không nhận được kết quả xử lý video.")

        # Export to CSV report
        progress(0.95, desc="Đang xuất file báo cáo...")
        export_success = export_to_csv(
            summary=summary,
            video_path=video_path,
            model_size=model_size,
            conf_moto=conf_motorcycle,
            conf_person=conf_person,
            output_csv_path=output_csv_path
        )

        # Format final results
        result_text = format_summary(summary)
        progress(1.0, desc="Hoàn thành!")
        
        if export_success:
            yield output_path, gr.update(visible=True), output_csv_path, result_text
        else:
            yield output_path, gr.update(visible=False), None, result_text

    except Exception as e:
        yield None, gr.update(visible=False), None, f"❌ Lỗi: {str(e)}"


# --- Build Gradio Interface ---

CUSTOM_CSS = """
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}
.header-text {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2em;
    font-weight: bold;
    margin-bottom: 0.5em;
}
.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 1.5em;
}
"""

with gr.Blocks(
    title="🏍️ Motorcycle Counter - Dem Xe May & Nguoi",
) as app:

    # Header
    gr.HTML("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       font-size: 2.5em; margin-bottom: 10px;">
                🏍️ Motorcycle & Rider Counter
            </h1>
            <p style="color: #888; font-size: 1.1em;">
                Đếm xe máy và số người ngồi trên xe bằng AI
                <br>Sử dụng YOLOv8 + Supervision | Hỗ trợ phát hiện chở quá tải
            </p>
        </div>
    """)

    with gr.Row():
        # Left column: Input
        with gr.Column(scale=1):
            gr.Markdown("### 📤 Upload Video")
            video_input = gr.File(
                label="Chọn video cần phân tích (MP4, MOV, AVI, MKV)",
                file_types=[".mp4", ".mov", ".avi", ".mkv"],
            )

            gr.Markdown("### ⚙️ Cài đặt")
            model_size = gr.Dropdown(
                choices=[
                    ("YOLOv8 Nano (nhanh nhất)", "yolov8n.pt"),
                    ("YOLOv8 Small", "yolov8s.pt"),
                    ("YOLOv8 Medium", "yolov8m.pt"),
                    ("YOLOv8 Large (khuyên dùng)", "yolov8l.pt"),
                    ("YOLOv8 XLarge (chính xác nhất)", "yolov8x.pt"),
                ],
                value="yolov8l.pt",
                label="🤖 Model AI",
                info="Model lớn hơn = chính xác hơn nhưng chậm hơn",
            )

            conf_motorcycle = gr.Slider(
                minimum=0.1,
                maximum=0.9,
                value=0.20,
                step=0.05,
                label="🎯 Độ tin cậy Xe máy (Conf Motorcycle)",
                info="Ngưỡng phát hiện xe máy. Nên để thấp (0.20 - 0.25) để bám vết tốt.",
            )

            conf_person = gr.Slider(
                minimum=0.1,
                maximum=0.9,
                value=0.30,
                step=0.05,
                label="🧑‍🤝‍🧑 Độ tin cậy Người (Conf Person)",
                info="Ngưỡng phát hiện người ngồi. Nên để cao hơn (0.30 - 0.35) để tránh đếm nhầm.",
            )

            track_buffer = gr.Slider(
                minimum=10,
                maximum=150,
                value=60,
                step=10,
                label="⏳ Lịch sử bám vết (Track Buffer)",
                info="Số frame ghi nhớ xe bị che khuất. Khuyên dùng 60 - 90 frame.",
            )

            imgsz = gr.Dropdown(
                choices=[
                    ("640px (Mặc định)", 640),
                    ("960px", 960),
                    ("1080px (Chính xác nhất nhưng chậm)", 1080),
                    ("1280px (Cực đại độ phân giải)", 1280),
                ],
                value=640,
                label="🖼️ Kích thước ảnh đầu vào (Inference Size)",
                info="Tăng lên 960/1080 khi dùng model XLarge để bắt xe máy ở rất xa.",
            )

            nms_iou = gr.Slider(
                minimum=0.1,
                maximum=0.9,
                value=0.7,
                step=0.05,
                label="🔀 Độ trùng lặp NMS (IoU)",
                info="Tăng lên 0.7 - 0.8 để hỗ trợ nhận diện xe chở 2 người tốt hơn (khuyên dùng 0.7)",
            )

            line_position = gr.Slider(
                minimum=0.1,
                maximum=0.9,
                value=0.5,
                step=0.05,
                label="📏 Vị trí vạch đếm mặc định (Line Position)",
                info="Chỉ áp dụng khi sử dụng vạch mặc định. 0.0 = trên cùng, 1.0 = dưới cùng.",
            )

            use_custom_line = gr.Checkbox(
                label="📐 Sử dụng vạch vẽ tùy chỉnh (Custom drawn line)",
                value=False,
                info="Bật để sử dụng vạch vẽ tự do ở tab bên phải thay cho vạch ngang mặc định."
            )

            count_mode = gr.Radio(
                choices=[
                    ("Đếm qua vạch (Line Crossing)", "line"),
                    ("Đếm tất cả xe phát hiện", "all"),
                ],
                value="line",
                label="📊 Chế độ đếm",
                info="'Đếm qua vạch' chính xác hơn cho camera cố định",
            )

            process_btn = gr.Button(
                "🚀 Bắt đầu phân tích",
                variant="primary",
                size="lg",
            )

        # Right column: Output & Calibration
        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.TabItem("🎬 Kết quả"):
                    video_output = gr.Video(
                        label="Video đã được xử lý",
                    )

                    with gr.Column(visible=False) as report_area:
                        gr.Markdown("### 📥 Tải xuống báo cáo")
                        csv_output = gr.File(
                            label="Báo cáo chi tiết CSV (mở bằng Excel)",
                            interactive=False,
                        )

                    gr.Markdown("### 📊 Kết quả đếm")
                    result_text = gr.Textbox(
                        label="Chi tiết thống kê",
                        lines=15,
                        max_lines=25,
                    )
                    
                with gr.TabItem("📏 Vẽ vạch đếm"):
                    gr.Markdown("### 🎨 Vẽ vạch đếm trực tiếp lên hình ảnh")
                    gr.Markdown(
                        "1. Upload video ở cột bên trái.\n"
                        "2. Chọn công cụ cọ vẽ (Brush) bên dưới hình và vẽ một nét thẳng làm vạch đếm trên làn đường.\n"
                        "3. Tích chọn 'Sử dụng vạch vẽ tùy chỉnh (Custom drawn line)' ở cột trái trước khi phân tích."
                    )
                    image_editor = gr.ImageEditor(
                        label="Ảnh chụp khung hình đầu tiên của video",
                        type="numpy",
                        height=500,
                        transforms=None,
                    )

    # Examples section
    gr.Markdown("""
    ---
    ### 📖 Hướng dẫn sử dụng
    1. **Upload video** quay từ camera giao thông hoặc camera an ninh
    2. **Chọn kiểu vạch**: Sử dụng vạch mặc định hoặc vạch tự vẽ (tích checkbox ở cột trái)
    3. **Tự vẽ vạch**: Chuyển sang tab "Vẽ vạch đếm" bên phải, dùng cọ vẽ một nét thẳng trên làn đường cần đếm
    4. **Nhấn "Bắt đầu phân tích"** ở cột trái và đợi kết quả
    """)

    # Event handlers
    video_input.change(
        fn=load_first_frame_into_editor,
        inputs=video_input,
        outputs=image_editor,
    )

    process_btn.click(
        fn=process_video,
        inputs=[
            video_input,
            model_size,
            conf_motorcycle,
            conf_person,
            nms_iou,
            line_position,
            use_custom_line,
            image_editor,
            count_mode,
            track_buffer,
            imgsz,
        ],
        outputs=[video_output, report_area, csv_output, result_text],
        concurrency_limit=None,
    )


if __name__ == "__main__":
    import socket

    def find_free_port(start=7860, end=7870):
        """Find the first available port in range."""
        for port in range(start, end + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("0.0.0.0", port))
                    return port
            except OSError:
                continue
        return start  # fallback

    port = find_free_port()
    print(f"\n🌐 Khoi dong tai: http://localhost:{port}\n")

    app.queue().launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True,
        inbrowser=True,
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(
            primary_hue="violet",
            secondary_hue="blue",
        ),
    )
