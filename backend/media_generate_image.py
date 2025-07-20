import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_image_with_ai(prompt, output_path):
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(image_response.content)
            return True
        return False
    except Exception as e:
        print(f"Error en generate_image_with_ai: {e}")
        return False
