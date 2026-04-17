import base64
from io import BytesIO
from PIL import Image
import json
from ScanAndSave.config import client, MODEL_NAME

class BaseAgent:
    def __init__(self, schema, schema_name="ResponseSchema"):
        self.client = client
        self.model = MODEL_NAME
        
        self.response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": schema
            }
        }

    def _encode_image(self, image: Image.Image) -> str:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def generate(self, system_prompt: str, input_data):
        user_content = []

        if isinstance(input_data, str):
            user_content.append({"type": "text", "text": input_data})
            
        elif isinstance(input_data, Image.Image):
            base64_image = self._encode_image(input_data)
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format=self.response_format,
            temperature=0.0
        )
        return response.choices[0].message.content