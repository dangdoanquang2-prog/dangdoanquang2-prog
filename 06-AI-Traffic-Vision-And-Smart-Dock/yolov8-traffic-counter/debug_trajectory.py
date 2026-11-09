import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv

video_path = "phulam_15s.mp4"
cap = cv2.VideoCapture(video_path)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
cap.release()

print(f"Video resolution: {w}x{h}, FPS: {fps}")

# Define lines to test
# Line A: 0.6031 0.7518 0.7250 1.0000 (User's drawn line on 960x540 canvas)
line_a_start = (int(w * 0.6031), int(h * 0.7518))
line_a_end = (int(w * 0.7250), int(h * 1.0000))

# Line B: 0.3349 0.2685 0.5828 0.4509 (Red line extracted from user's output video)
line_b_start = (int(w * 0.3349), int(h * 0.2685))
line_b_end = (int(w * 0.5828), int(h * 0.4509))

print(f"Line A (Normalized 0.6031 0.7518 0.7250 1.0000): {line_a_start} to {line_a_end}")
print(f"Line B (Normalized 0.3349 0.2685 0.5828 0.4509): {line_b_start} to {line_b_end}")

model = YOLO("yolov8n.pt")
tracker = sv.ByteTrack(track_activation_threshold=0.15, lost_track_buffer=60)

cap = cv2.VideoCapture(video_path)
frame_idx = 0

history_x = {}
history_y = {}
history_frames = {}

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

active_tids = set()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_idx += 1
    
    results = model(frame, verbose=False, imgsz=640)[0]
    
    moto_boxes = []
    moto_confs = []
    for box in results.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        if cls == 3 and conf >= 0.20:
            xyxy = box.xyxy[0].cpu().numpy()
            moto_boxes.append(xyxy)
            moto_confs.append(conf)
            
    if len(moto_boxes) > 0:
        detections = sv.Detections(
            xyxy=np.array(moto_boxes),
            confidence=np.array(moto_confs),
            class_id=np.array([3] * len(moto_boxes))
        )
        tracked = tracker.update_with_detections(detections)
        
        if len(tracked) > 0 and tracked.tracker_id is not None:
            for i in range(len(tracked)):
                tid = int(tracked.tracker_id[i])
                bbox = tracked.xyxy[i]
                cx = (bbox[0] + bbox[2]) / 2
                cy = (bbox[1] + bbox[3]) / 2
                
                if tid not in history_x:
                    history_x[tid] = []
                    history_y[tid] = []
                    history_frames[tid] = []
                    
                history_x[tid].append(cx)
                history_y[tid].append(cy)
                history_frames[tid].append(frame_idx)
                active_tids.add(tid)
                
                # Check intersection on Line A
                if len(history_x[tid]) >= 2:
                    p_prev = (history_x[tid][-2], history_y[tid][-2])
                    p_curr = (history_x[tid][-1], history_y[tid][-1])
                    if intersect(p_prev, p_curr, line_a_start, line_a_end):
                        print(f"Frame {frame_idx:3d} | ID {tid:3d} crossed LINE A! Point: {p_curr}")
                    if intersect(p_prev, p_curr, line_b_start, line_b_end):
                        print(f"Frame {frame_idx:3d} | ID {tid:3d} crossed LINE B! Point: {p_curr}")

cap.release()

print("\n--- Summary of all tracked IDs ---")
print(f"Total unique IDs tracked: {len(active_tids)}")
for tid in sorted(active_tids):
    xs = history_x[tid]
    ys = history_y[tid]
    fs = history_frames[tid]
    print(f"ID {tid:3d}: frame {fs[0]:3d} to {fs[-1]:3d} | Start ({xs[0]:.1f}, {ys[0]:.1f}) -> End ({xs[-1]:.1f}, {ys[-1]:.1f})")
