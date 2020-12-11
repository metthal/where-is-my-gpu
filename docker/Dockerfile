FROM python:3.9 AS builder

ADD requirements.txt /app/
RUN pip wheel --no-cache-dir -r /app/requirements.txt -w /wheels

FROM python:3.9-slim

COPY --from=builder /wheels /wheels
RUN pip install wheels/*

ADD . /app
WORKDIR /app

ENV TZ=Europe/Prague
ENTRYPOINT ["bash", "/app/docker/entrypoint.sh"]
