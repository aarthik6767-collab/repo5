import os

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai

from chatbot_config import SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite"

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured in the .env file.")

client = genai.Client(api_key=API_KEY)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Please enter a message."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "temperature": 0.3,
                "max_output_tokens": 1024,
            },
        )

        answer = (response.text or "").strip()

        if not answer:
            return jsonify({"error": "I couldn't generate a response. Please try again."}), 502

        return jsonify({"answer": answer})

    except Exception:
        return jsonify({
            "error": "The AI service is temporarily unavailable. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
