from typing import Dict

from openai import OpenAI
from openai import AuthenticationError


class ImageCaptionController:

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.prompt = "provide a simple, neutral caption for this image"

    def get_caption_for_image(self, image_url: str) -> str:
        try:
            response = self._call_openai_api(image_url)
            return response.choices[0].message.content
        except AuthenticationError:
            raise Exception("Invalid OpenAI API key/ no API key provided.")

    def _call_openai_api(self, image_url: str):  # TODO: add union type
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


