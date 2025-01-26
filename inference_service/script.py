#!/usr/bin/env python3

import os
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image

# 1. Model & labels URL
MODEL_URL = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4"
LABELS_URL = "https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt"

os.environ["TFHUB_CACHE_DIR"] = "/app/model_cache"

# 2. Load the model from TF Hub
print("Loading MobileNetV2 model from TensorFlow Hub...")
model = hub.load(MODEL_URL)

# 3. Download the ImageNet labels
print("Downloading labels...")
labels_path = tf.keras.utils.get_file("ImageNetLabels.txt", LABELS_URL)
with open(labels_path, "r") as f:
    imagenet_labels = f.read().splitlines()


def load_image(image_path, image_size=(224, 224)):
    img = Image.open(image_path).convert("RGB")
    img = img.resize(image_size)
    img = np.array(img) / 255.0
    # Cast to float32
    img = img.astype(np.float32)
    # Add the batch dimension
    img = np.expand_dims(img, axis=0)
    return img


def classify_image(image_path):
    """Classify the image and print top 5 predictions."""
    img_tensor = load_image(image_path)
    predictions = model(img_tensor).numpy().squeeze()  # shape (1001,)

    # Get top 5 predictions
    top_5_indices = predictions.argsort()[-5:][::-1]

    print(f"\nClassifying image: {image_path}")
    print("Top 5 Predictions:")
    for i in top_5_indices:
        class_name = imagenet_labels[i]
        score = predictions[i]
        print(f"  {class_name:<20} (score: {score:.4f})")


if __name__ == "__main__":
    # Replace with your actual image file path
    image_path = "cat.jpg"

    if not os.path.exists(image_path):
        print(f"ERROR: '{image_path}' not found. Please provide a valid image path.")
    else:
        classify_image(image_path)
