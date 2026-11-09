import cv2
import numpy as np
from collections import defaultdict
import supervision as sv
from motorcycle_counter import MotorcyclePersonCounter

# Load video
video_path = "test_10s.mp4"
video_info = sv.VideoInfo.from_video_path(video_path)
print(f"Video FPS: {video_info.fps}, Total Frames: {video_info.total_frames}, Resolution: {video_info.width}x{video_info.height}")

# Initialize counter with our updated code
counter = MotorcyclePersonCounter(
    model_size="yolov8l.pt",
    conf_motorcycle=0.20,
    conf_person=0.30,
    iou_threshold=0.7,
    track_buffer=60,
    imgsz=640
)

# Custom line zone tracking
w, h = video_info.width, video_info.height
line_y_ratio = 0.5  # middle of screen
line_start = sv.Point(0, int(h * line_y_ratio))
line_end = sv.Point(w, int(h * line_y_ratio))
line_zone = sv.LineZone(start=line_start, end=line_end)

tracker = sv.ByteTrack(frame_rate=video_info.fps, track_activation_threshold=0.20, lost_track_buffer=60)
frame_generator = sv.get_video_frames_generator(video_path)

for frame_idx, frame in enumerate(frame_generator):
    results = counter.model(
        frame,
        conf=0.20,
        iou=0.7,
        verbose=False,
        classes=[0, 3],
    )[0]
    detections = sv.Detections.from_ultralytics(results)
    
    # Filter motorcycles
    moto_mask = (detections.class_id == 3) & (detections.confidence >= 0.20)
    moto_dets = detections[moto_mask]
    
    # Track
    moto_dets = tracker.update_with_detections(moto_dets)
    
    if len(moto_dets) > 0 and moto_dets.tracker_id is not None:
        crossed_in, crossed_out = line_zone.trigger(detections=moto_dets)
        
        for i, tracker_id in enumerate(moto_dets.tracker_id):
            tid = int(tracker_id)
            bbox = moto_dets.xyxy[i]
            # Bottom-center coordinate
            bc_x = (bbox[0] + bbox[2]) / 2
            bc_y = bbox[3]
            
            # Print if it's near the line or crosses
            dist_to_line = abs(bc_y - (h * line_y_ratio))
            if dist_to_line < 50 or crossed_in[i] or crossed_out[i]:
                print(f"Frame {frame_idx:03d} | ID {tid:2d} | Bbox Bottom Y: {bc_y:5.1f} | Line Y: {h*line_y_ratio:5.1f} | Crossed In: {crossed_in[i]} | Crossed Out: {crossed_out[i]}")
