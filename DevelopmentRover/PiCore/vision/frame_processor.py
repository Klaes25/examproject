import cv2 as cv
from vision import color_detection


class FrameProcessor:

    def __init__(self, detect_colors=None):
        self.detect_colors = detect_colors

    def process(self, frame):
        # blurs an image using a Gaussian filter
        # when both sigma values are set to zero, they are calculated from the kernel size
        blurred = cv.GaussianBlur(frame, (5, 5), 0)

        results = {}

        if self.detect_colors is not None:
            results["colors"] = color_detection.detect(blurred, self.detect_colors)

        return results
