import cv2

# ==========================================================
# CLASS COLOR MAP (BGR - OpenCV format)
# ==========================================================
CLASS_COLORS = {
    "Car": (0, 200, 0),
    "Truck": (0, 140, 255),
    "Tram": (180, 0, 255),
    "Pedestrian": (255, 120, 0)
}

# ==========================================================
# BOUNDING BOX DRAW FUNCTION
# ==========================================================

def draw_pro_box(frame, bbox, class_name, track_id, lane_id):

    x1, y1, x2, y2 = map(int, bbox)
    color = CLASS_COLORS.get(class_name, (0, 255, 0))

    h, w = frame.shape[:2]

    # Dynamic scaling (resolution aware)
    line_thickness = max(2, int(h / 500))
    font_scale = h / 1080 * 0.6
    font_thickness = max(1, int(h / 800))

    # ------------------------------------------------------
    # 1️⃣ Draw bounding box
    # ------------------------------------------------------
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, line_thickness)

    # ------------------------------------------------------
    # 2️⃣ Prepare multi-line label
    # ------------------------------------------------------
    label_lines = [
        f"{class_name}",
        f"ID: {track_id}",
        f"Lane: {lane_id}"
    ]

    # Calculate text sizes
    text_sizes = [
        cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale, font_thickness)[0]
        for line in label_lines
    ]

    text_width = max(size[0] for size in text_sizes)
    text_height = sum(size[1] + 6 for size in text_sizes)

    padding = 6

    # Default: label above box
    bg_x1 = x1
    bg_y1 = y1 - text_height - 2 * padding
    bg_x2 = x1 + text_width + 2 * padding
    bg_y2 = y1

    # If not enough space above → place below box
    if bg_y1 < 0:
        bg_y1 = y1
        bg_y2 = y1 + text_height + 2 * padding

    # ------------------------------------------------------
    # 3️⃣ Draw filled background
    # ------------------------------------------------------
    # Transparency factor (0.0 - 1.0)
    alpha = 0.6  

    # Create overlay copy
    overlay = frame.copy()

    # Draw full colour on overlay
    cv2.rectangle(overlay, (bg_x1, bg_y1),
                (bg_x2, bg_y2), color, -1)

    # Merge overlay with original frame

    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # ------------------------------------------------------
    # 4️⃣ Draw shadow + white text
    # ------------------------------------------------------
    y_offset = bg_y1 + padding

    for line in label_lines:
        (tw, th), _ = cv2.getTextSize(
            line,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            font_thickness
        )

        y_offset += th

        # Shadow
        cv2.putText(
            frame,
            line,
            (bg_x1 + padding + 1, y_offset + 1),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (0, 0, 0),
            font_thickness + 1,
            cv2.LINE_AA
        )

        # Main text
        cv2.putText(
            frame,
            line,
            (bg_x1 + padding, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            font_thickness,
            cv2.LINE_AA
        )

        y_offset += 6

#----------------------------
# HUD
#----------------------------
def draw_hud(frame, class_counts, lane_counts):

    x_start = 20
    y_start = 40
    line_spacing = 26
    top_padding = 20
    bottom_padding = 35



    class_order = ["Car", "Truck", "Tram", "Pedestrian"]
    lane_order = ["1", "2", "3", "4", "side1", "side2"]

    total_lines = 1 + len(class_order) + len(lane_order)
    panel_height = top_padding + total_lines * line_spacing + bottom_padding
    panel_width = 340

    # ---- Transparent panel ----
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (10, 10),
        (10 + panel_width, 10 + panel_height),
        (40, 40, 40),
        -1
    )

    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    # ---- Border ----
    cv2.rectangle(
        frame,
        (10, 10),
        (10 + panel_width, 10 + panel_height),
        (180, 180, 180),
        1
    )

    y = top_padding + 20

    cv2.putText(frame, "Traffic Summary",
                (x_start, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2, cv2.LINE_AA)

    y += line_spacing * 2

    # ---- Class counts ----
    for cls in class_order:
        count = class_counts.get(cls, 0)
        text = f"{cls}s: {count}"
        cv2.putText(frame, text,
                    (x_start, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 255), 1, cv2.LINE_AA)
        y += line_spacing

    y += line_spacing // 2

    # ---- Lane counts ----
    for lane in lane_order:
        count = lane_counts.get(lane, 0)
        text = f"Lane {lane}: {count}"
        cv2.putText(frame, text,
                    (x_start, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 255), 1, cv2.LINE_AA)
        y += line_spacing