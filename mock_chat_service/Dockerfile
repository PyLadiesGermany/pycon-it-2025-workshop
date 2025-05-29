# Dockerfile.mock_llm_service
FROM python:3.12-slim

# 1. Install runtime deps
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 2. Set working dir
WORKDIR /app

# 3. Install Python dependencies
#    We only need Flask, python-dotenv and the OpenAI client
RUN pip install --no-cache-dir \
    flask \
    python-dotenv \
    openai

# 4. Copy service code 
COPY ./mock_chat.py .  

# 5. Expose the port your service listens on
EXPOSE 8002

# 6. Launch the service
#    (If your code ends with: app.run(host="0.0.0.0", port=8002))
CMD ["python", "mock_chat.py"]