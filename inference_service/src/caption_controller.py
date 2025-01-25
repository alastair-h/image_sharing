from typing import Dict

from openai import OpenAI


class ImageCaptionController:

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.prompt = "provide a simple, neutral caption for this image"

    def get_caption_for_image(self, image_url: str) -> str:
        response = self.client.chat.completions.create(
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
        return response.choices[0].message.content


