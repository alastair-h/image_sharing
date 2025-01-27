from dependency_injector import containers, providers

from src.controllers.caption_controller import ImageCaptionController
from src.controllers.classifier_controller import ImageClassificationController
import os

MODEL_URL = os.getenv("MODEL_URL")
LABELS_URL = os.getenv("LABELS_URL")
API_KEY = os.getenv("OPENAI_API_KEY")


class AppContainer(containers.DeclarativeContainer):
    image_classification_controller = providers.Singleton(
        ImageClassificationController,
        model_url=MODEL_URL,
        labels_url=LABELS_URL,
    )

    image_caption_controller = providers.Singleton(
        ImageCaptionController,
        api_key=API_KEY,
    )


app_container = AppContainer()
