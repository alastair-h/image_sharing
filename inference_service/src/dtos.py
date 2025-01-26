from pydantic import BaseModel


class ImageUrl(BaseModel):
    image_url: str  # can't send url as url paramater obviously


class ClassificationResult(BaseModel):
    class_name: str
    score: float


class ClassificationResponse(BaseModel):
    results: list[ClassificationResult]
    inference_time_ms: float


class CaptionResponse(BaseModel):
    caption: str
    inference_time_ms: float