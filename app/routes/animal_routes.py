import base64
import re
import os
import requests
from io import BytesIO
from PIL import Image
from flask import Blueprint, request, jsonify
import google.generativeai as genai
import json

animal_bp = Blueprint('animal_bp', __name__)

def get_animal_photo(animal_name: str) -> str | None:
    """Fetch a photo of the animal from Unsplash."""
    access_key = os.getenv('UNSPLASH_ACCESS_KEY')
    if not access_key:
        print("Warning: UNSPLASH_ACCESS_KEY not set. Skipping image fetch.")
        return None
    
    url = f"https://api.unsplash.com/search/photos"
    params = {
        'query': animal_name,
        'per_page': 1,
        'orientation': 'landscape'
    }
    headers = {
        'Authorization': f'Client-ID {access_key}'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']
    except requests.RequestException as e:
        print(f"Error fetching image from Unsplash: {e}")
        return None
    return None

@animal_bp.route('/animal', methods=['POST'])
def find_spirit_animal():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({"error": "No image data provided"}), 400

    try:
        # Create an in-memory image object
        image_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(image_bytes))

        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = """**РОЛЬ И ЗАДАЧА:**
Твоя роль — остроумный, современный оракул. Твоя задача — проанализировать человека на фото и вернуть валидный JSON-объект.

**ПРАВИЛА:**
1.  Отвечай ТОЛЬКО валидным JSON-объектом. Никакого лишнего текста.
2.  Поля `animal` и `reason` должны быть на русском языке.
3.  Поле `animal_en` должно содержать точный перевод `animal` на английский для поиска в API.

**СТРУКТУРА JSON-ОТВЕТА:**
{
  "animal": "string (на русском)",
  "animal_en": "string (на английском)",
  "reason": "string (на русском)"
}

Проанализируй изображение и сгенерируй JSON.
"""

        response = model.generate_content([prompt, img])
        
        # Clean up the response to ensure it's valid JSON
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        
        analysis_data = json.loads(cleaned_response_text)

        # Fetch photo from Unsplash
        animal_en = analysis_data.get('animal_en')
        image_url = get_animal_photo(animal_en) if animal_en else None
        analysis_data['imageUrl'] = image_url

        return jsonify(analysis_data)

    except Exception as e:
        print(f"Error processing image or calling Gemini: {e}")
        return jsonify({"error": str(e)}), 500 