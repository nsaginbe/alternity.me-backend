import json
from flask import Blueprint, request, jsonify
import google.generativeai as genai

mbti_bp = Blueprint('mbti_bp', __name__)

@mbti_bp.route('/mbti', methods=['POST'])
def mbti_analysis():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    answers = data.get('answers')
    gender = data.get('gender', 'Not specified')
    questions_text = data.get('questionsText', {})

    if not answers or not questions_text:
        return jsonify({"error": "Missing answers or questions text"}), 400

    full_answers_context = [
        {"question": questions_text.get(ans.get('id')), "answer_value": ans.get('value')}
        for ans in answers
    ]

    prompt = f"""
    **ROLE & OBJECTIVE:** You are an expert MBTI analyst. Your task is to analyze the user's test answers and return a JSON object.
    **IMPORTANT:** You MUST respond ONLY with a valid JSON object. Do not include "```json", "```", or any other text outside of the JSON structure.

    **USER DATA:**
    - Gender: {gender}
    - Answers: {json.dumps(full_answers_context, indent=2)}

    **JSON OUTPUT STRUCTURE:**
    {{
    "mbti_type": "string", // The 4-letter MBTI type (e.g., "INFP")
    "type_name": "string", // The descriptive name (e.g., "The Mediator")
    "core_characteristics": "string", // A single, concise paragraph (max 3 sentences).
    "strengths": ["string", "string", "string"], // Exactly 3 key strengths.
    "challenges": ["string", "string", "string"], // Exactly 3 potential challenges.
    "career_paths": ["string", "string", "string"], // Exactly 3 suitable career examples.
    "famous_people": [  // Exactly 3 well-known people who share the same MBTI type.
        {{
        "name": "string", // Full name of the person or fictional character.
        "description": "string" // Short phrase describing why they are known (e.g., "Theoretical physicist", "Pop singer", "Fictional detective from BBC's Sherlock")
        }}
    ],
    "summary": "string" // A final, encouraging summary sentence.
    }}

    **NOTES FOR famous_people FIELD:**
    - Include a mix of real people and fictional characters if appropriate.
    - Prefer globally recognized names (e.g., Albert Einstein, Steve Jobs, Sherlock Holmes, etc.).
    - Make the descriptions clear and short, max 10 words.

    Analyze the data and generate the JSON object now.
    """

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # Clean up the response to ensure it's valid JSON
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        
        analysis_data = json.loads(cleaned_response_text)

        # Add the official link based on the determined type
        mbti_type_lower = analysis_data.get("mbti_type", "").lower()
        if mbti_type_lower:
            analysis_data["official_link"] = f"https://www.16personalities.com/{mbti_type_lower}-personality"
        else:
            analysis_data["official_link"] = "https://www.16personalities.com/"


        return jsonify(analysis_data)

    except Exception as e:
        print(f"Error during API call or JSON parsing: {e}")
        return jsonify({"error": f"Failed to analyze personality: {e}"}), 500 