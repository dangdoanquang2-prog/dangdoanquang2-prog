"""
Motorcycle Counter - Command Line Interface
============================================
Process video files from the command line.

Usage:
    python main.py --input video.mp4
    python main.py --input video.mp4 --model yolov8x.pt --confidence 0.4
    python main.py --input video.mp4 --mode all --line 0.5
"""

import argparse
import os
import sys

# Prepend local bin folder containing ffmpeg/ffprobe to PATH
bin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
if os.path.exists(bin_path):
    os.environ["PATH"] = bin_path + os.path.pathsep + os.environ["PATH"]

import time
from motorcycle_counter import MotorcyclePersonCounter, format_summary, export_to_csv


def main():
    parser = argparse.ArgumentParser(
        description="🏍️ Motorcycle & Rider Counter - Dem xe may va nguoi ngoi tren xe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input traffic.mp4
  python main.py --input traffic.mp4 --model yolov8x.pt --confidence 0.4
  python main.py --input traffic.mp4 --mode all --no-output
  python main.py --input traffic.mp4 --line 0.3 --output result.mp4
        """,
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to input video file",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to output annotated video (default: output/result_<input>.mp4)",
    )
    parser.add_argument(
        "--no-output",
        action="store_true",
        help="Do not save annotated video (faster processing)",
    )
    parser.add_argument(
        "--model", "-m",
        default="yolov8l.pt",
        choices=["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt"],
        help="YOLOv8 model size (default: yolov8l.pt)",
    )
    parser.add_argument(
        "--confidence", "-c",
        type=float,
        default=None,
        help="General confidence threshold (acts as fallback if specific thresholds are not set)",
    )
    parser.add_argument(
        "--conf-motorcycle",
        type=float,
        default=0.20,
        help="Confidence threshold specifically for motorcycles (default: 0.20)",
    )
    parser.add_argument(
        "--conf-person",
        type=float,
        default=0.30,
        help="Confidence threshold specifically for persons (default: 0.30)",
    )
    parser.add_argument(
        "--track-buffer",
        type=int,
        default=60,
        help="Number of frames for ByteTrack to remember lost tracks (default: 60)",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Inference image size (default: 640)",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.7,
        help="NMS IoU threshold (default: 0.7)",
    )
    parser.add_argument(
        "--line", "-l",
        type=float,
        default=0.5,
        help="Counting line vertical position, 0.0=top 1.0=bottom (default: 0.5)",
    )
    parser.add_argument(
        "--line-coords",
        type=float,
        nargs=4,
        default=None,
        help="Custom line coordinates (x1 y1 x2 y2) normalized from 0.0 to 1.0",
    )
    parser.add_argument(
        "--mode",
        choices=["line", "all"],
        default="line",
        help="Counting mode: 'line' for line crossing, 'all' for all detected (default: line)",
    )
    parser.add_argument(
        "--export-csv", "-e",
        default=None,
        help="Path to save CSV report of results",
    )

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.input):
        print(f"❌ Error: Video file not found: {args.input}")
        sys.exit(1)

    # Setup output path
    output_path = None
    if not args.no_output:
        if args.output:
            output_path = args.output
        else:
            os.makedirs("output", exist_ok=True)
            base = os.path.basename(args.input).rsplit(".", 1)[0]
            output_path = os.path.join("output", f"result_{base}.mp4")

    # Progress display
    def show_progress(current, total):
        pct = current / total * 100 if total > 0 else 0
        bar_len = 40
        filled = int(bar_len * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\r  [{bar}] {pct:.1f}% ({current}/{total} frames)", end="", flush=True)

    # Run
    print("=" * 55)
    print("  🏍️  MOTORCYCLE & RIDER COUNTER")
    print("=" * 55)
    print(f"  Input:            {args.input}")
    print(f"  Model:            {args.model}")
    print(f"  Conf Motorcycle:  {args.conf_motorcycle}")
    print(f"  Conf Person:      {args.conf_person}")
    print(f"  NMS IoU:          {args.iou}")
    print(f"  Track Buffer:     {args.track_buffer} frames")
    print(f"  Inference Size:   {args.imgsz}px")
    print(f"  Line pos:         {args.line}")
    print(f"  Mode:             {args.mode}")
    print(f"  Output:           {output_path or 'None (no-output mode)'}")
    print("=" * 55)
    print()

    print(f"  Loading model {args.model}...")
    start_time = time.time()

    counter = MotorcyclePersonCounter(
        model_size=args.model,
        confidence=args.confidence,
        iou_threshold=args.iou,
        conf_motorcycle=args.conf_motorcycle,
        conf_person=args.conf_person,
        track_buffer=args.track_buffer,
        imgsz=args.imgsz,
    )

    print(f"  Model loaded. Processing video...")
    print()

    summary = counter.process_video(
        video_path=args.input,
        output_path=output_path,
        line_y_ratio=args.line,
        count_mode=args.mode,
        line_coords=args.line_coords,
        progress_callback=show_progress,
    )

    elapsed = time.time() - start_time
    print()
    print()

    # Print results
    print(format_summary(summary))
    print()
    print(f"  ⏱️  Thoi gian xu ly: {elapsed:.1f} giay")

    if output_path:
        print(f"  📁 Video ket qua: {output_path}")

    if args.export_csv:
        print(f"  📊 Dang xuat file bao cao CSV ra: {args.export_csv}...")
        success = export_to_csv(
            summary=summary,
            video_path=args.input,
            model_size=args.model,
            conf_moto=args.conf_motorcycle,
            conf_person=args.conf_person,
            output_csv_path=args.export_csv
        )
        if success:
            print("  ✓ Xuat file bao cao CSV thanh cong!")
        else:
            print("  ✗ Xuat file bao cao CSV that bai!")

    print()


if __name__ == "__main__":
    main()
