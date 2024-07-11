FROM python:3.11-alpine

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code
COPY ./web /code/web

CMD ["python", "-m", "polman.cli.main", "app"]
