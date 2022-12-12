FROM python:3.9-slim

RUN python -m pip install requests redis

COPY ./app /app

CMD [ "python", "/app/particle.py" ]
