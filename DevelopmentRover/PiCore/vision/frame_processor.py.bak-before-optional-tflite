import cv2 as cv
from vision import color_detection
from vision.object_detection import ObjectDetector

_MARGIN = 10  # pixels
_ROW_SIZE = 10  # pixels
_FONT_SIZE = 1
_FONT_THICKNESS = 1
_TEXT_COLOR = (255, 0, 0)  # red


class FrameProcessor:

    def __init__(self, detect_colors=None, detect_objects=False):
        self.detect_colors = detect_colors
        self.detector = ObjectDetector() if detect_objects else None

    def process(self, frame):
        # blurs an image using a Gaussian filter
        # when both sigma values are set to zero, they are calculated from the kernel size
        blurred = cv.GaussianBlur(frame, (5, 5), 0)

        annotated = frame.copy()
        results = {}

        if self.detect_colors is not None:
            results["colors"] = color_detection.detect(blurred, self.detect_colors)
            for obj in results["colors"]:
                x, y, w, h = obj["bbox"]
                # Draw bounding_box
                cv.rectangle(annotated, (x, y), (x + w, y + h), _TEXT_COLOR, 3)
                # Draw label and score
                cv.putText(annotated, obj["color"],
                           (_MARGIN + x, _MARGIN + _ROW_SIZE + y),
                           cv.FONT_HERSHEY_PLAIN, _FONT_SIZE, _TEXT_COLOR, _FONT_THICKNESS)

        if self.detector is not None:
            results["objects"] = self.detector.detect(blurred)
            for obj in results["objects"]:
                x, y, w, h = obj["bbox"]
                # Draw bounding_box
                cv.rectangle(annotated, (x, y), (x + w, y + h), _TEXT_COLOR, 3)
                # Draw label and score
                result_text = obj["label"] + ' (' + str(obj["score"]) + ')'
                cv.putText(annotated, result_text,
                           (_MARGIN + x, _MARGIN + _ROW_SIZE + y),
                           cv.FONT_HERSHEY_PLAIN, _FONT_SIZE, _TEXT_COLOR, _FONT_THICKNESS)

        return annotated, results
