import json
import cv2
import os
import sys
from tqdm import tqdm
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, root_dir)

from src.visualization.overlay import draw_pro_box, draw_hud


# Project root folder
project_root = root_dir

json_path = os.path.join(project_root, "annotations", "instances_default.json")
frames_folder = os.path.join(project_root, "frames")
output_video_path = os.path.join(project_root, "output_ground_truth.mp4")


# Load COCO
with open(json_path, "r") as f:
    coco_data = json.load(f)

images = coco_data["images"]
annotations = coco_data["annotations"]
categories = coco_data["categories"]

# Category mapping
category_map = {cat["id"]: cat["name"] for cat in categories}


# Mapping image_id -> annotations list
image_annotations = {}
for ann in annotations:
    image_annotations.setdefault(ann["image_id"], []).append(ann)

# Pretpostavljamo 1080p
width = images[0]["width"]
height = images[0]["height"]

# Video writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps = 29.97
out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

print("Generating video...")

# ===============================
# TRACKING STATISTICS STORAGE
# ===============================

unique_ids = set()
class_counts = {}
lane_counts = {}

for img_info in tqdm(images):

    image_id = img_info["id"]
    frame_number = image_id
    file_name = f"{frame_number:06d}.jpg"
    image_path = os.path.join(frames_folder, file_name)

    frame = cv2.imread(image_path)

    if frame is None:
        print("Missing frame:", image_path)
        continue

    # --- Loop through annotations ---
    for ann in image_annotations.get(image_id, []):

        x, y, w, h = ann["bbox"]
        class_name = category_map[ann["category_id"]]

        attributes = ann.get("attributes", {})
        track_id = attributes.get("track_id", "N/A")
        lane_id = attributes.get("Lane_id", "N/A")

        # ---- Update statistics (only once per unique ID) ----
        if track_id not in unique_ids and track_id != "N/A":
            unique_ids.add(track_id)
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            lane_counts[lane_id] = lane_counts.get(lane_id, 0) + 1

        # ---- Always draw bounding box ----
        x, y, w, h = int(x), int(y), int(w), int(h)
        bbox = (x, y, x + w, y + h)

        draw_pro_box(
            frame,
            bbox,
            class_name,
            track_id,
            lane_id
        )

    # ---- Draw HUD once per frame ----
    draw_hud(frame, class_counts, lane_counts)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    (text_width, text_height), _ = cv2.getTextSize(
        timestamp,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        2
    )

    x = frame.shape[1] - text_width - 20
    y = 40

    # shadow
    cv2.putText(frame, timestamp,
                (x+1, y+1),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,0,0),
                2,
                cv2.LINE_AA)

    # main text
    cv2.putText(frame, timestamp,
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255,255,255),
                2,
                cv2.LINE_AA)
    out.write(frame)

out.release()
print("Video saved as output_ground_truth.mp4")