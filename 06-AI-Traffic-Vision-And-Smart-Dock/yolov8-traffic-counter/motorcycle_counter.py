"""
Motorcycle & Person Counter using YOLOv8 + Supervision
=====================================================
Core logic for detecting motorcycles, tracking them,
associating riders, and counting.
"""

import cv2
import numpy as np
from collections import defaultdict
from statistics import mode, median
from ultralytics import YOLO
import supervision as sv

# COCO class IDs
PERSON_CLASS_ID = 0
MOTORCYCLE_CLASS_ID = 3

# Color palette (BGR format)
COLORS = {
    "motorcycle": (0, 200, 255),   # Orange
    "person": (255, 150, 0),       # Blue
    "line": (0, 255, 0),           # Green
    "text_bg": (30, 30, 30),       # Dark gray
    "text": (255, 255, 255),       # White
    "warning": (0, 0, 255),        # Red - for overloaded
}


class MotorcyclePersonCounter:
    """
    Detects motorcycles and persons in video frames,
    tracks motorcycles across frames, associates riders,
    and counts motorcycles crossing a virtual line.
    """

    def __init__(
        self,
        model_size="yolov8l.pt",
        confidence=None,
        iou_threshold=0.7,
        conf_motorcycle=0.20,
        conf_person=0.30,
        track_buffer=60,
        imgsz=640,
    ):
        """
        Args:
            model_size: YOLOv8 model variant (n/s/m/l/x)
            confidence: General confidence (used if conf_motorcycle/conf_person are not set)
            iou_threshold: NMS IoU threshold
            conf_motorcycle: Confidence threshold specifically for motorcycles
            conf_person: Confidence threshold specifically for persons
            track_buffer: Number of frames for ByteTrack to remember lost tracks
            imgsz: Inference image size (e.g. 640, 960, 1280)
        """
        self.model = YOLO(model_size)
        self.iou_threshold = iou_threshold
        
        # Split confidence thresholds
        self.conf_motorcycle = conf_motorcycle if conf_motorcycle is not None else (confidence or 0.20)
        self.conf_person = conf_person if conf_person is not None else (confidence or 0.30)
        self.track_buffer = track_buffer
        self.imgsz = imgsz
        
        # Customizable passenger association thresholds
        self.min_ioa = 0.20
        self.min_dist_score = 0.35
        self.min_association_score = 0.12

    def process_video(
        self,
        video_path: str,
        output_path: str = None,
        line_y_ratio: float = 0.6,
        count_mode: str = "line",
        line_coords: list = None,
        progress_callback=None,
    ) -> dict:
        """
        Process a video file and count motorcycles + riders.

        Args:
            video_path: Path to input video
            output_path: Path to save annotated output video
            line_y_ratio: Vertical position of counting line (0.0=top, 1.0=bottom)
            count_mode: "line" for line crossing, "all" for all unique tracked
            progress_callback: Optional callback(current_frame, total_frames)

        Returns:
            Dictionary with counting results and statistics
        """
        # --- Setup ---
        video_info = sv.VideoInfo.from_video_path(video_path)
        total_frames = video_info.total_frames or 0
        w, h = video_info.width, video_info.height

        # Tracker - tuned lost_track_buffer and track_activation_threshold
        tracker_activation_threshold = max(0.12, self.conf_motorcycle - 0.05)
        tracker = sv.ByteTrack(
            frame_rate=video_info.fps,
            track_activation_threshold=tracker_activation_threshold,
            lost_track_buffer=self.track_buffer,
        )

        # Counting line (custom coords or default horizontal line)
        if line_coords is not None and len(line_coords) == 4:
            x1_ratio, y1_ratio, x2_ratio, y2_ratio = line_coords
            line_start = sv.Point(int(w * x1_ratio), int(h * y1_ratio))
            line_end = sv.Point(int(w * x2_ratio), int(h * y2_ratio))
        else:
            line_start = sv.Point(0, int(h * line_y_ratio))
            line_end = sv.Point(w, int(h * line_y_ratio))
            
        line_zone = sv.LineZone(
            start=line_start,
            end=line_end,
        )

        # Annotators
        box_annotator = sv.BoxAnnotator(
            thickness=2,
        )
        label_annotator = sv.LabelAnnotator(
            text_scale=0.6,
            text_thickness=1,
            text_padding=5,
        )
        line_annotator = sv.LineZoneAnnotator(
            thickness=3,
            text_scale=1.0,
            text_thickness=2,
            display_in_count=False,
            display_out_count=False,
        )


        # Tracking data
        # For each motorcycle tracker_id, store list of person counts per frame
        motorcycle_person_history = defaultdict(list)
        # Store y-coordinate history to track movement direction
        motorcycle_y_history = defaultdict(list)
        # Store x-coordinate history to track movement center
        motorcycle_x_history = defaultdict(list)
        # Store frame history to track first/last detection frame
        motorcycle_frame_history = defaultdict(list)
        # Set of tracker_ids that crossed the line
        line_crossed_ids = set()
        # Track historical crossing events for de-duplication: list of dicts {"frame_idx", "x", "y", "id"}
        crossed_events = []

        # --- Process Frames ---
        frame_generator = sv.get_video_frames_generator(video_path)

        def _process_frames(sink=None):
            """Inner function to process all frames, optionally writing to sink."""
            for frame_idx, frame in enumerate(frame_generator):
                # Progress callback
                if progress_callback and total_frames > 0:
                    progress_callback(frame_idx, total_frames)

                # --- Detection ---
                # Run YOLO with the lower of the two confidence thresholds, and the configured image size
                min_conf = min(self.conf_motorcycle, self.conf_person)
                results = self.model(
                    frame,
                    conf=min_conf,
                    iou=self.iou_threshold,
                    verbose=False,
                    classes=[PERSON_CLASS_ID, MOTORCYCLE_CLASS_ID],
                    imgsz=self.imgsz,
                )[0]
                detections = sv.Detections.from_ultralytics(results)

                # --- Separate classes and filter by individual confidence thresholds ---
                if len(detections) > 0 and detections.confidence is not None:
                    person_mask = (detections.class_id == PERSON_CLASS_ID) & (detections.confidence >= self.conf_person)
                    moto_mask = (detections.class_id == MOTORCYCLE_CLASS_ID) & (detections.confidence >= self.conf_motorcycle)
                else:
                    person_mask = detections.class_id == PERSON_CLASS_ID
                    moto_mask = detections.class_id == MOTORCYCLE_CLASS_ID

                person_dets = detections[person_mask]
                moto_dets = detections[moto_mask]

                # --- Track motorcycles ---
                moto_dets = tracker.update_with_detections(moto_dets)

                # --- Associate persons to motorcycles ---
                if len(moto_dets) > 0 and moto_dets.tracker_id is not None:
                    person_counts = self._associate_persons_to_motorcycles(
                        moto_dets.xyxy, person_dets.xyxy if len(person_dets) > 0 else np.array([])
                    )

                    for i, tracker_id in enumerate(moto_dets.tracker_id):
                        tid = int(tracker_id)
                        motorcycle_person_history[tid].append(person_counts[i])
                        # Track coordinates of centroid to determine direction & trajectory
                        bbox = moto_dets.xyxy[i]
                        cx = (bbox[0] + bbox[2]) / 2
                        cy = (bbox[1] + bbox[3]) / 2
                        motorcycle_x_history[tid].append(cx)
                        motorcycle_y_history[tid].append(cy)
                        motorcycle_frame_history[tid].append(frame_idx)

                    # --- Line crossing detection ---
                    if count_mode == "line":
                        # We still call trigger to let LineZone draw its internal states/arrows if needed
                        _ = line_zone.trigger(detections=moto_dets)
                        
                        for i in range(len(moto_dets)):
                            tid = int(moto_dets.tracker_id[i])
                            bbox = moto_dets.xyxy[i]
                            cx = (bbox[0] + bbox[2]) / 2
                            cy = (bbox[1] + bbox[3]) / 2
                            
                            x_vals = motorcycle_x_history[tid]
                            y_vals = motorcycle_y_history[tid]
                            if len(y_vals) >= 2:
                                x_prev = x_vals[-2]
                                y_prev = y_vals[-2]
                                x_curr = x_vals[-1]
                                y_curr = y_vals[-1]
                                
                                # Trajectory crossing condition: segment AB intersects virtual line segment CD
                                pt_c = (line_start.x, line_start.y)
                                pt_d = (line_end.x, line_end.y)
                                crossed = self._check_intersection(
                                    (x_prev, y_prev), (x_curr, y_curr), pt_c, pt_d
                                )
                                
                                if crossed:
                                    # Check duplicate crossings
                                    is_duplicate = False
                                    
                                    # 1. ID-Lock Check: if ID has crossed before, it is always a duplicate
                                    if tid in line_crossed_ids:
                                        is_duplicate = True
                                    else:
                                        # 2. Spatio-Temporal Check for ID switches (only for extremely close time & space)
                                        for event in crossed_events:
                                            frame_diff = frame_idx - event["frame_idx"]
                                            if frame_diff > 8: # Only check last 8 frames (~0.3s)
                                                continue
                                                
                                            # Calculate normalized spatial distance
                                            dx = (cx - event["x"]) / w
                                            dy = (cy - event["y"]) / h
                                            dist = np.sqrt(dx**2 + dy**2)
                                            
                                            # If another crossing happened extremely close in time (< 8 frames) and space (< 3% screen size)
                                            if dist < 0.03:
                                                is_duplicate = True
                                                break
                                                    
                                    if not is_duplicate:
                                        line_crossed_ids.add(tid)
                                        crossed_events.append({
                                            "frame_idx": frame_idx,
                                            "x": cx,
                                            "y": cy,
                                            "id": tid
                                        })

                # --- Annotate frame ---
                if sink is not None:
                    annotated = frame.copy()


                    # Draw motorcycle boxes with person count labels
                    active_ids = []
                    if len(moto_dets) > 0 and moto_dets.tracker_id is not None:
                        active_ids = list(moto_dets.tracker_id)
                        labels = []
                        for i, tracker_id in enumerate(moto_dets.tracker_id):
                            tid = int(tracker_id)
                            pc = self._get_stable_person_count(motorcycle_person_history[tid]) if tid in motorcycle_person_history else 1
                            label = f"Moto #{tid} | {pc} nguoi"
                            if pc >= 3:
                                label += " [QUA TAI!]"
                            labels.append(label)

                        annotated = box_annotator.annotate(annotated, moto_dets)
                        annotated = label_annotator.annotate(annotated, moto_dets, labels=labels)

                    # Draw person boxes
                    if len(person_dets) > 0:
                        annotated = box_annotator.annotate(annotated, person_dets)

                    # Draw counting line
                    if count_mode == "line":
                        annotated = line_annotator.annotate(annotated, line_zone)

                    # Draw stats overlay
                    annotated = self._draw_stats_overlay(
                        annotated, motorcycle_person_history, line_crossed_ids, count_mode, active_tracker_ids=active_ids
                    )

                    sink.write_frame(annotated)

        # Execute frame processing
        if output_path:
            with sv.VideoSink(output_path, video_info, codec='avc1') as sink:
                _process_frames(sink)
        else:
            _process_frames(sink=None)

        # --- Generate Summary ---
        summary = self._generate_summary(
            motorcycle_person_history,
            line_crossed_ids,
            count_mode,
            motorcycle_y_history,
            crossed_events=crossed_events,
            motorcycle_frames=motorcycle_frame_history,
            fps=video_info.fps or 30.0
        )

        return summary

    def _check_intersection(self, A, B, C, D):
        """Check if segment AB intersects segment CD."""
        def ccw(p1, p2, p3):
            return (p3[1]-p1[1]) * (p2[0]-p1[0]) > (p2[1]-p1[1]) * (p3[0]-p1[0])
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

    def _associate_persons_to_motorcycles(
        self, moto_bboxes: np.ndarray, person_bboxes: np.ndarray
    ) -> list:
        """
        Associate each detected person to the best-matching motorcycle
        based on bounding box overlap (IoA - Intersection over Area of person).

        Args:
            moto_bboxes: (N, 4) motorcycle bounding boxes [x1, y1, x2, y2]
            person_bboxes: (M, 4) person bounding boxes [x1, y1, x2, y2]

        Returns:
            List of person counts for each motorcycle
        """
        n_motos = len(moto_bboxes)
        person_counts = [0] * n_motos

        if len(person_bboxes) == 0:
            # No persons detected, assume 1 driver per motorcycle
            return [1] * n_motos

        for person_bbox in person_bboxes:
            px1, py1, px2, py2 = person_bbox
            person_area = (px2 - px1) * (py2 - py1)
            if person_area <= 0:
                continue

            best_moto_idx = -1
            best_score = 0

            for j, moto_bbox in enumerate(moto_bboxes):
                mx1, my1, mx2, my2 = moto_bbox
                mw = mx2 - mx1
                mh = my2 - my1

                # Spatial pre-filter: 
                # 1. Person bottom should not be significantly lower than motorcycle bottom (pedestrian check)
                if py2 > my2 + 0.15 * mh:
                    continue
                # 2. Person top should not be too far down the motorcycle (noise check)
                if py1 > my1 + 0.6 * mh:
                    continue

                # Calculate intersection
                ix1 = max(px1, mx1)
                iy1 = max(py1, my1)
                ix2 = min(px2, mx2)
                iy2 = min(py2, my2)

                if ix1 >= ix2 or iy1 >= iy2:
                    continue

                intersection = (ix2 - ix1) * (iy2 - iy1)
                ioa = intersection / person_area  # Intersection over person Area

                # Calculate centers
                px_center = (px1 + px2) / 2
                py_center = (py1 + py2) / 2
                mx_center = (mx1 + mx2) / 2
                my_center = (my1 + my2) / 2

                # Normalize distance: penalize horizontal offset more than vertical
                dist_x = abs(px_center - mx_center) / (mw + 1e-6)
                dist_y = abs(py_center - my_center) / (mh + 1e-6)
                norm_dist = np.sqrt((dist_x * 1.5)**2 + dist_y**2)

                # Distance score decreases as the distance increases
                dist_score = 1.0 / (1.0 + norm_dist)

                # Combined score: IoA weighted by center proximity
                score = ioa * dist_score

                # We require a minimum overlap and reasonable proximity
                if ioa > self.min_ioa and dist_score > self.min_dist_score:
                    if score > best_score:
                        best_score = score
                        best_moto_idx = j

            # Assign person to motorcycle if overall score is good
            if best_moto_idx >= 0 and best_score > self.min_association_score:
                person_counts[best_moto_idx] += 1

        # Ensure at least 1 person (driver) per motorcycle
        return [max(c, 1) for c in person_counts]

    def _get_stable_person_count(self, history: list) -> int:
        """
        Get the most stable (reliable) person count from frame history.
        Filters out transient detection drops and outliers by taking the maximum 
        value that appears in at least a certain percentage of the frames.
        This percentage is dynamically adjusted based on the length of the history.
        """
        if not history:
            return 1

        total = len(history)
        # Dynamic ratio threshold:
        # For short tracks (< 15 frames), require higher consistency (30%) to avoid false detections
        # For long tracks (>= 15 frames), use more lenient threshold (15%)
        if total < 15:
            min_ratio = 0.30
        else:
            min_ratio = 0.15

        # Count frequencies
        freqs = {}
        for x in history:
            freqs[x] = freqs.get(x, 0) + 1

        # Find the highest passenger count that represents a significant portion of tracking
        candidates = [val for val, count in freqs.items() if count / total >= min_ratio]
        if candidates:
            return int(max(candidates))

        # Fallback to mode or median
        try:
            return int(mode(history))
        except Exception:
            return int(round(median(history)))

    def _generate_summary(
        self,
        motorcycle_person_history: dict,
        line_crossed_ids: set,
        count_mode: str,
        motorcycle_y_history: dict = None,
        crossed_events: list = None,
        motorcycle_frames: dict = None,
        fps: float = 30.0,
    ) -> dict:
        """Generate final counting summary."""

        if motorcycle_y_history is None:
            motorcycle_y_history = {}
        if crossed_events is None:
            crossed_events = []
        if motorcycle_frames is None:
            motorcycle_frames = {}

        # Determine which motorcycles to count
        if count_mode == "line":
            counted_ids = line_crossed_ids
        else:
            # Only count motorcycles that have been tracked for at least 12 frames (0.4s at 30fps)
            counted_ids = set()
            for tid, history in motorcycle_person_history.items():
                if len(history) >= 12:
                    counted_ids.add(tid)

        # Get stable person count for each counted motorcycle
        motorcycle_riders = {}
        for tid in counted_ids:
            if tid in motorcycle_person_history:
                motorcycle_riders[tid] = self._get_stable_person_count(
                    motorcycle_person_history[tid]
                )
            else:
                motorcycle_riders[tid] = 1

        total_motorcycles = len(motorcycle_riders)

        # Breakdown by person count
        breakdown = defaultdict(int)
        for tid, person_count in motorcycle_riders.items():
            breakdown[person_count] += 1

        # Sort breakdown
        breakdown = dict(sorted(breakdown.items()))

        # Total persons
        total_persons = sum(
            count * n_motos for count, n_motos in breakdown.items()
        )

        # Overloaded (3+ persons)
        overloaded = sum(
            n_motos for count, n_motos in breakdown.items() if count >= 3
        )

        # Build detailed logs sorted chronologically
        detailed_logs = []
        
        def get_sort_key(tid):
            if count_mode == "line":
                for event in crossed_events:
                    if event["id"] == tid:
                        return event["frame_idx"]
            if tid in motorcycle_frames and motorcycle_frames[tid]:
                return motorcycle_frames[tid][0]
            return 0

        sorted_counted_ids = sorted(list(counted_ids), key=get_sort_key)

        for i, tid in enumerate(sorted_counted_ids):
            pc = motorcycle_riders.get(tid, 1)
            
            # Find frame index
            frame_idx = 0
            if count_mode == "line":
                for event in crossed_events:
                    if event["id"] == tid:
                        frame_idx = event["frame_idx"]
                        break
            else:
                if tid in motorcycle_frames and motorcycle_frames[tid]:
                    frame_idx = motorcycle_frames[tid][0]
            
            timestamp = round(frame_idx / fps, 2)
            status = "Qua tai" if pc >= 3 else "Binh thuong"
            
            detailed_logs.append({
                "stt": i + 1,
                "id": tid,
                "frame": frame_idx,
                "timestamp": timestamp,
                "riders": pc,
                "status": status
            })

        summary = {
            "total_motorcycles": total_motorcycles,
            "total_persons": total_persons,
            "breakdown": breakdown,
            "overloaded_count": overloaded,
            "details": motorcycle_riders,
            "count_mode": count_mode,
            "detailed_logs": detailed_logs,
        }

        return summary

    def _draw_stats_overlay(
        self, frame, motorcycle_person_history, line_crossed_ids, count_mode, active_tracker_ids=None
    ):
        """Draw real-time statistics overlay on frame."""
        h, w = frame.shape[:2]

        # Calculate current stats
        if count_mode == "line":
            total = len(line_crossed_ids)
            counted_ids = line_crossed_ids
        else:
            total = len(motorcycle_person_history)
            counted_ids = set(motorcycle_person_history.keys())

        # Count breakdown of riders
        counts = {1: 0, 2: 0, 3: 0, 4: 0} # 4 represents 4 or more
        for tid in counted_ids:
            if tid in motorcycle_person_history:
                pc = self._get_stable_person_count(motorcycle_person_history[tid])
            else:
                pc = 1
            if pc >= 4:
                counts[4] += 1
            elif pc in counts:
                counts[pc] += 1
            else:
                counts[1] += 1

        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (380, 240), COLORS["text_bg"], -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Draw text
        cv2.putText(
            frame, f"XE MAY DA DEM: {total}",
            (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS["motorcycle"], 2
        )
        
        cv2.putText(
            frame, f"Xe 1 nguoi: {counts[1]}",
            (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLORS["text"], 1
        )
        cv2.putText(
            frame, f"Xe 2 nguoi: {counts[2]}",
            (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLORS["text"], 1
        )
        
        # Use warning color (Red) if there are overloaded vehicles
        color_3 = COLORS["warning"] if counts[3] > 0 else COLORS["text"]
        cv2.putText(
            frame, f"Xe 3 nguoi: {counts[3]}",
            (20, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color_3, 1
        )
        
        color_4 = COLORS["warning"] if counts[4] > 0 else COLORS["text"]
        cv2.putText(
            frame, f"Xe >= 4 nguoi: {counts[4]}",
            (20, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color_4, 1
        )

        active_count = len(active_tracker_ids) if active_tracker_ids is not None else 0
        cv2.putText(
            frame, f"Dang theo doi (hien tai): {active_count} xe",
            (20, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1
        )

        mode_text = "LINE CROSSING" if count_mode == "line" else "ALL TRACKED"
        cv2.putText(
            frame, f"Mode: {mode_text}",
            (20, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1
        )

        return frame


def export_to_csv(summary: dict, video_path: str, model_size: str, conf_moto: float, conf_person: float, output_csv_path: str):
    """
    Export summary and detailed logs to a CSV file.
    Uses utf-8-sig encoding for proper Excel Vietnamese character support.
    """
    import csv
    import datetime
    import os

    try:
        with open(output_csv_path, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 1. Write Header / Metadata
            writer.writerow(["BÁO CÁO THỐNG KÊ ĐẾM XE MÁY & NGƯỜI"])
            writer.writerow(["Thời gian xuất báo cáo", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow(["Video nguồn", os.path.basename(video_path)])
            writer.writerow(["Model AI", model_size])
            writer.writerow(["Độ tin cậy xe máy", conf_moto])
            writer.writerow(["Độ tin cậy người", conf_person])
            writer.writerow([])
            
            # 2. Write Summary
            writer.writerow(["TỔNG QUAN KẾT QUẢ"])
            mode_label = "Đếm qua vạch" if summary["count_mode"] == "line" else "Tất cả xe phát hiện"
            writer.writerow(["Chế độ đếm", mode_label])
            writer.writerow(["Tổng số xe máy", summary["total_motorcycles"]])
            writer.writerow(["Tổng số người", summary["total_persons"]])
            
            # Overloaded ratio
            overloaded = summary["overloaded_count"]
            total_motos = summary["total_motorcycles"]
            ratio = (overloaded / total_motos * 100) if total_motos > 0 else 0.0
            writer.writerow(["Số xe chở quá tải (>=3 người)", f"{overloaded} ({ratio:.2f}%)"])
            writer.writerow([])
            
            # Breakdown
            writer.writerow(["PHÂN LOẠI CHI TIẾT"])
            for person_count, moto_count in sorted(summary["breakdown"].items()):
                writer.writerow([f"Xe chở {person_count} người", f"{moto_count} xe"])
            writer.writerow([])
            
            # 3. Write Detailed Logs
            writer.writerow(["NHẬT KÝ CHI TIẾT TỪNG XE"])
            writer.writerow(["STT", "ID Xe", "Khung hình (Frame)", "Thời điểm (Giây)", "Số người ngồi trên xe", "Trạng thái"])
            
            for log in summary.get("detailed_logs", []):
                writer.writerow([
                    log["stt"],
                    log["id"],
                    log["frame"],
                    log["timestamp"],
                    log["riders"],
                    log["status"]
                ])
        return True
    except Exception as e:
        print(f"Error exporting CSV: {e}")
        return False


def format_summary(summary: dict) -> str:
    """Format summary dictionary into a readable Vietnamese string."""
    lines = []
    lines.append("=" * 50)
    lines.append("   KET QUA DEM XE MAY & NGUOI NGOI TREN XE")
    lines.append("=" * 50)
    lines.append("")

    mode_label = "Dem qua vach" if summary["count_mode"] == "line" else "Tat ca xe phat hien"
    lines.append(f"  Che do dem: {mode_label}")
    lines.append(f"  Tong so xe may: {summary['total_motorcycles']}")
    lines.append(f"  Tong so nguoi: {summary['total_persons']}")
    lines.append("")

    lines.append("  CHI TIET:")
    lines.append("  " + "-" * 40)
    for person_count, moto_count in sorted(summary["breakdown"].items()):
        emoji = "🏍️" if person_count <= 2 else "⚠️"
        lines.append(f"  {emoji}  {moto_count} xe may co {person_count} nguoi")
    lines.append("  " + "-" * 40)

    if summary["overloaded_count"] > 0:
        lines.append("")
        lines.append(f"  ⚠️  CANH BAO: {summary['overloaded_count']} xe cho qua tai (>= 3 nguoi)!")

    lines.append("")
    lines.append("=" * 50)

    return "\n".join(lines)
