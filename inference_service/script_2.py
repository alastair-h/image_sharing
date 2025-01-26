from src.controller import ImageClassificationController


if __name__ == "__main__":
    image_path = "cat.jpg"
    controller = ImageClassificationController()
    controller.load_model()
    controller.download_labels()
    controller.classify_image(image_path)