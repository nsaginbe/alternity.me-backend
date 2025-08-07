import base64
from io import BytesIO
from PIL import Image
from flask import Blueprint, request, jsonify
import google.generativeai as genai
import json

color_bp = Blueprint('color_bp', __name__)

@color_bp.route('/color', methods=['POST'])
def analyze_color():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({"error": "No image data provided"}), 400

    try:
        image_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(image_bytes))

        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = """**РОЛЬ И ЗАДАЧА:**
Твоя роль — колорист и арт-критик с поэтическим взглядом. Твоя задача — проанализировать цветовую палитру и атмосферу изображения и вернуть валидный JSON-объект.

**ПРАВИЛА:**
1.  Отвечай ТОЛЬКО валидным JSON-объектом. Никакого лишнего текста.
2.  Все текстовые поля (`mood_name`, `description`) должны быть на русском языке.
3.  `mood_name`: Придумай короткое, образное и красивое название для цветового настроения фото (например, "Неоновый закат", "Утренняя дымка в лесу", "Осенний уют").
4.  `description`: Напиши поэтичное и вдохновляющее описание (2-3 предложения), перечисляя, с чем ассоциируются эти цвета. (например, "Эта палитра напоминает о теплом пледе, чашке какао и мурлыканье кота...")
5.  `palette`: Извлеки ровно 4 доминирующих цвета из изображения и верни их в виде массива HEX-кодов.

**СТРУКТУРА JSON-ОТВЕТА:**
{
  "mood_name": "string",
  "description": "string",
  "palette": ["#XXXXXX", "#XXXXXX", "#XXXXXX", "#XXXXXX"]
}

Проанализируй изображение и сгенерируй JSON.
"""

        response = model.generate_content([prompt, img])
        
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        
        analysis_data = json.loads(cleaned_response_text)

        return jsonify(analysis_data)

    except Exception as e:
        print(f"Error processing image or calling Gemini: {e}")
        return jsonify({"error": str(e)}), 500 