FROM debian:latest

RUN apt update && apt install -y redis-server

COPY redis.conf /redis.conf

CMD ["redis-server", "redis.conf"]
