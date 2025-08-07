import os
import google.generativeai as genai
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")

    # Import and register blueprints
    from .routes.mbti_routes import mbti_bp
    from .routes.animal_routes import animal_bp

    app.register_blueprint(mbti_bp)
    app.register_blueprint(animal_bp)

    return app 