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

# The line coords from the video (approximated from phulam_frame_2.png)
# Top dot: (x=579, y=406) -> ratios: x1_ratio = 579/960 = 0.6031, y1_ratio = 406/540 = 0.7518
# Bottom dot: (x=696, y=540) -> ratios: x2_ratio = 696/960 = 0.7250, y2_ratio = 540/540 = 1.0000
# Let's verify by plotting
x1_ratio, y1_ratio, x2_ratio, y2_ratio = 0.6031, 0.7518, 0.7250, 1.0000
line_start = (int(w * x1_ratio), int(h * y1_ratio))
line_end = (int(w * x2_ratio), int(h * y2_ratio))

print(f"Video resolution: {w}x{h}, FPS: {fps}")
print(f"Line segment: {line_start} to {line_end}")

model = YOLO("yolov8x.pt")
tracker = sv.ByteTrack(track_activation_threshold=0.15, lost_track_buffer=60)

cap = cv2.VideoCapture(video_path)
frame_idx = 0

history_x = {}
history_y = {}
history_frames = {}

target_ids = {119, 134, 157, 131, 162, 164}
crossings = []

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

while True:
    ret, frame = cap.read()
    if not ret or frame_idx >= 270:
        break
    frame_idx += 1
    
    if frame_idx % 20 == 0:
        print(f"Processing frame {frame_idx}/270...")
        
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
                
                if len(history_x[tid]) >= 2:
                    p_prev = (history_x[tid][-2], history_y[tid][-2])
                    p_curr = (history_x[tid][-1], history_y[tid][-1])
                    crossed = intersect(p_prev, p_curr, line_start, line_end)
                    if crossed:
                        crossings.append((tid, frame_idx, p_prev, p_curr))
                        print(f"ID {tid} CROSSED at frame {frame_idx}: {p_prev} -> {p_curr}")

cap.release()

print("\n--- Detailed trajectory check for target IDs ---")
for tid in target_ids:
    if tid not in history_x:
        print(f"ID {tid}: Never tracked in this run!")
        continue
    xs = history_x[tid]
    ys = history_y[tid]
    fs = history_frames[tid]
    print(f"ID {tid}: Tracked for {len(xs)} frames. Frames {fs[0]} to {fs[-1]}")
    print(f"  First point: ({xs[0]:.1f}, {ys[0]:.1f})")
    print(f"  Last point: ({xs[-1]:.1f}, {ys[-1]:.1f})")
    has_crossed = False
    for i in range(1, len(xs)):
        p_prev = (xs[i-1], ys[i-1])
        p_curr = (xs[i], ys[i])
        if intersect(p_prev, p_curr, line_start, line_end):
            has_crossed = True
            print(f"  -> INTERSECTED line at frame {fs[i]}: {p_prev} -> {p_curr}")
    if not has_crossed:
        print("  -> No intersection detected with the line!")
