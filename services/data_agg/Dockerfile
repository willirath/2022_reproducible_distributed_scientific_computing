FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

RUN python -m pip install requests asciichartpy pandas numpy redis

COPY ./app /app
