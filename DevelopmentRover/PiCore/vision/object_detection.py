# Copyright 2021 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "1.tflite")


class ObjectDetector:

    def __init__(self, model_path=MODEL_PATH, num_threads=4, score_threshold=0.3, max_results=3):
        # Initialize the object detection model
        base_options = core.BaseOptions(
            file_name=model_path, use_coral=False, num_threads=num_threads)
        detection_options = processor.DetectionOptions(
            max_results=max_results, score_threshold=score_threshold)
        options = vision.ObjectDetectorOptions(
            base_options=base_options, detection_options=detection_options)
        self.detector = vision.ObjectDetector.create_from_options(options)

    def detect(self, frame_rgb):
        # Create a TensorImage object from the RGB image.
        input_tensor = vision.TensorImage.create_from_array(frame_rgb)

        # Run object detection estimation using the model.
        detection_result = self.detector.detect(input_tensor)

        results = []
        for detection in detection_result.detections:
            bbox = detection.bounding_box
            x = bbox.origin_x
            y = bbox.origin_y
            w = bbox.width
            h = bbox.height

            category = detection.categories[0]
            label = category.category_name
            score = round(category.score, 2)

            results.append({
                "label":    label,
                "score":    score,
                "centroid": (x + w // 2, y + h // 2),
                "bbox":     (x, y, w, h),
            })

        return results
