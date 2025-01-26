from openai import OpenAI

client = OpenAI(api_key="")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "provide a simple, neutral caption for this image"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://i.natgeofe.com/n/4cebbf38-5df4-4ed0-864a-4ebeb64d33a4/NationalGeographic_1468962_16x9.jpg",
                    },
                },
            ],
        }
    ],
    max_tokens=300,
)

print(response.choices[0])
