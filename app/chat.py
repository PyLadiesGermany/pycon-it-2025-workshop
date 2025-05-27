# write functions which take a canned input for openai gpt-4o-mini model


import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from openai import OpenAI
from openai.error import OpenAIError

load_dotenv()
app = Flask(__name__)
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")
openai_client = OpenAI(api_key=openai_api_key)


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        if not data or "messages" not in data:
            return jsonify({"error": "Invalid input"}), 400

        messages = data["messages"]
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, max_tokens=150, temperature=0.7
        )

        return jsonify(response.choices[0].message)

    except OpenAIError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500
