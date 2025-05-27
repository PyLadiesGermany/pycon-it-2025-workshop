# write mock LLM service that simulates the OpenAI API
import random
from flask import Flask, request, jsonify
from openai.error import OpenAIError
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        if not data or "messages" not in data:
            return jsonify({"error": "Invalid input"}), 400

        messages = data["messages"]
        # Simulate a random response
        if random.random() < 0.1:  # 10% chance to simulate an error
            raise OpenAIError("Simulated error for testing purposes")

        response = {
            "id": "chatcmpl-1234567890",
            "object": "chat.completion",
            "created": int(random.time()),
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"Mock response to: {messages[-1]['content']}",
                    },
                    "finish_reason": "stop",
                }
            ],
        }

        return jsonify(response)

    except OpenAIError as e:
        return jsonify({"error": str(e)}), 500
    except Exception:
        return jsonify({"error": "An unexpected error occurred"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
