from http import HTTPStatus

from fastapi import HTTPException
from openai import AuthenticationError
from openai import OpenAI


class ImageCaptionController:

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.prompt = "provide a simple, neutral caption for this image"

    def get_caption_for_image(self, image_url: str) -> str:
        try:
            response = self._call_openai_api(image_url)
            return response.choices[0].message.content
        except AuthenticationError:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid or missing OpenAI API key.")

    def _call_openai_api(self, image_url: str):
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )


