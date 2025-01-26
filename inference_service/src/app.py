import time

from fastapi import FastAPI

from src.dependency_injection import app_container
from src.dtos import ImageUrl, ClassificationResponse, CaptionResponse

app = FastAPI()

@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}


@app.post("/classify", response_model=ClassificationResponse)
def classify_image(request: ImageUrl):
    start_time = time.perf_counter()  # TODO: use wrapper function
    results = app_container.image_classification_controller().classify_image(request.image_url)
    end_time = time.perf_counter()
    inference_time_ms = (end_time - start_time) * 1000.0

    return ClassificationResponse(results=results, inference_time_ms=inference_time_ms)


@app.post("/caption", response_model=CaptionResponse)
def caption_image(request: ImageUrl):
    start_time = time.perf_counter()
    caption = app_container.image_caption_controller().get_caption_for_image(request.image_url)
    end_time = time.perf_counter()
    inference_time_ms = (end_time - start_time) * 1000.0

    return CaptionResponse(caption=caption, inference_time_ms=inference_time_ms)
