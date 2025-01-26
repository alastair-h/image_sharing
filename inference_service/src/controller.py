from io import BytesIO

import numpy as np
import requests
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image
from fastapi import HTTPException
from http import HTTPStatus

from src.dtos import ClassificationResult


class ImageClassificationController:
    def __init__(self, model_url: str, labels_url: str):
        self.model_url = model_url
        self.labels_url = labels_url
        self.model = None
        self.labels = None
        self._load_model_and_labels()

    def classify_image(self, image_url: str) -> list[ClassificationResult]:

        pil_image = self._download_image_from_url(image_url)
        img_tensor = self._load_image_and_resize(pil_image)
        predictions = self.model(img_tensor).numpy().squeeze()

        top_indices = predictions.argsort()[-5:][::-1]  # get top 5 predictions

        results = []
        for i in top_indices:
            class_name = self.labels[i]
            score = float(predictions[i])
            results.append(ClassificationResult(class_name=class_name, score=score))
        return results

    def _load_model_and_labels(self):

        print("Loading MobileNetV2 model from TensorFlow Hub...")
        self.model = hub.load(self.model_url)

        print("Downloading ImageNet labels...")
        labels_path = tf.keras.utils.get_file("ImageNetLabels.txt", self.labels_url)
        with open(labels_path, "r") as f:
            self.labels = f.read().splitlines()

    @staticmethod
    def _download_image_from_url(image_url: str) -> Image.Image:

        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="Failed to download image from the provided URL.")

        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type.lower():
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="URL does not point to a valid image.")

        try:
            return Image.open(BytesIO(response.content)).convert("RGB")
        except Exception:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Unable to process the downloaded image.")

    @staticmethod
    def _load_image_and_resize(pil_image: Image.Image, image_size=(224, 224)) -> np.ndarray:

        img = pil_image.resize(image_size)
        img = np.array(img) / 255.0
        img = img.astype(np.float32)
        img = np.expand_dims(img, axis=0)
        return img
