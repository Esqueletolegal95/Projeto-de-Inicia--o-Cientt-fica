from label_studio_ml.model import LabelStudioMLBase
from ultralytics import YOLO
import numpy as np

class YOLOModel(LabelStudioMLBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = YOLO("best.pt")  # coloque seu modelo aqui
        self.labels = ["buy", "sell"]  # ajuste conforme seu projeto

    def predict(self, tasks, **kwargs):
        predictions = []
        for task in tasks:
            image_url = task["data"]["image"]
            results = self.model.predict(image_url)

            output = []
            for r in results[0].boxes:
                x1, y1, x2, y2 = r.xyxy[0].tolist()
                conf = float(r.conf[0])
                label = self.labels[int(r.cls[0])]

                output.append({
                    "from_name": "bbox",
                    "to_name": "image",
                    "type": "rectanglelabels",
                    "score": conf,
                    "value": {
                        "x": x1,
                        "y": y1,
                        "width": x2 - x1,
                        "height": y2 - y1,
                        "rectanglelabels": [label]
                    }
                })

            predictions.append({"result": output})
        return predictions
