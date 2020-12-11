FROM python:3.9

ADD requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

ADD . /app

WORKDIR /app

CMD ["/app/run.py"]
