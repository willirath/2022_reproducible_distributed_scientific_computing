FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim-2022-11-25

RUN python -m pip install requests asciichartpy pandas numpy redis

COPY ./app /app
