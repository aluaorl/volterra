FROM python:3.11.9

COPY ./requirements.txt /requirements.txt

RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir -r /requirements.txt
RUN pip3 install gunicorn

COPY ./app.py /code/
COPY ./calculation_engine.py /code/
COPY ./expression_parser.py /code/
COPY ./components /code/components/
RUN mkdir /code/assets
COPY ./assets/ /code/assets/

WORKDIR /code/
ENV PYTHONPATH /code

ENV GUNICORN_CMD_ARGS "--bind=0.0.0.0:8000 --workers=2 --threads=4 --worker-class=gthread --timeout=300 --forwarded-allow-ips='*' --access-logfile -"

CMD ["gunicorn", "app:server"]