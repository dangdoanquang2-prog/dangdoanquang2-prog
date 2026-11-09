import cv2
import os

video_path = "output_counted (3).mp4"
dest_dir = r"C:\Users\Dell\.gemini\antigravity\brain\4d70bf98-ab7e-4906-9773-054cdef19db8"
os.makedirs(dest_dir, exist_ok=True)

if not os.path.exists(video_path):
    print(f"Error: {video_path} does not exist!")
    exit(1)

cap = cv2.VideoCapture(video_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Video: {video_path}, Total Frames: {total_frames}, FPS: {fps}")

# Extract 4 frames evenly distributed
frame_indices = [
    int(total_frames * 0.1),
    int(total_frames * 0.3),
    int(total_frames * 0.6),
    int(total_frames * 0.9)
]

for idx, f_idx in enumerate(frame_indices):
    cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
    ret, frame = cap.read()
    if ret and frame is not None:
        out_path = os.path.join(dest_dir, f"phulam_frame_{idx+1}.png")
        cv2.imwrite(out_path, frame)
        print(f"Extracted frame {f_idx} to {out_path}")
    else:
        print(f"Failed to read frame {f_idx}")
cap.release()
