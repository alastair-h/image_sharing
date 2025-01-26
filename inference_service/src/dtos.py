from pydantic import BaseModel


class ClassificationRequest(BaseModel):
    image_url: str


class ClassificationResult(BaseModel):
    class_name: str
    score: float


class ClassificationResponse(BaseModel):
    results: list[ClassificationResult]
    inference_time_ms: float
