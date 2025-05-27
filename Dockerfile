FROM python:3.12-slim

RUN apt-get -y update && apt-get -y install gcc 

RUN pip install poetry \
    && poetry config virtualenvs.create false

RUN pip install torch==2.6.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu \
    --no-cache-dir

COPY ./pyproject.toml /
COPY ./poetry.lock /
RUN poetry install

COPY .env  /app/.env
COPY ./app /app

WORKDIR /app
EXPOSE 8001
CMD ["poetry", "run", "python", "main.py"]
