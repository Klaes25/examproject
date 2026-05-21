import cv2 as cv
import numpy as np

# Use [H-10, 100, 100] and [H+10, 255, 255] as lower and upper bounds.
# Hue range is [0, 179], saturation and value [0, 255] for 8-bit images.
COLOR_RANGES = {
    "red": [
        (np.array([0,   120, 70]),  np.array([10,  255, 255])),
        (np.array([170, 120, 70]),  np.array([180, 255, 255])),
    ],
    # green = np.uint8([[[0,255,0]]]) -> cvtColor BGR2HSV -> [[[60 255 255]]]
    "green": [
        (np.array([50,  100, 100]), np.array([70,  255, 255])),
    ],
    "blue": [
        (np.array([110, 50,  50]),  np.array([130, 255, 255])),
    ],
    "yellow": [
        (np.array([20,  100, 100]), np.array([35,  255, 255])),
    ],
}

MIN_CONTOUR_AREA = 500


def detect(frame_rgb, colors=None):
    # converts an image from one color space to another
    hsv = cv.cvtColor(frame_rgb, cv.COLOR_RGB2HSV)

    targets = colors if colors else list(COLOR_RANGES.keys())
    results = []

    for color in targets:
        if color not in COLOR_RANGES:
            continue

        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for (lower, upper) in COLOR_RANGES[color]:
            # checks if array elements lie between the elements of two other arrays
            mask |= cv.inRange(hsv, lower, upper)

        # findContours retrieves contours from the binary image
        # CHAIN_APPROX_SIMPLE removes all redundant points and compresses
        # the contour, thereby saving memory
        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv.contourArea(cnt)
            if area < MIN_CONTOUR_AREA:
                continue

            # (x, y) represents the top-left corner and (w, h) width and height dimensions
            x, y, w, h = cv.boundingRect(cnt)

            M = cv.moments(cnt)
            if M["m00"] == 0:
                continue
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            results.append({
                "color":    color,
                "centroid": (cx, cy),
                "bbox":     (x, y, w, h),
                "area":     int(area),
            })

    return results
