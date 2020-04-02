FROM python:3.8-alpine

ENV PYTHONUNBUFFERED=1

# DIR structure
WORKDIR /code

# Installing dependencies
COPY requirements.txt requirements.txt

# Extra system packages installed for building python packages
RUN apk add --no-cache --virtual .build-deps gcc musl-dev && \
    pip install --disable-pip-version-check --no-cache-dir -r requirements.txt && \
    apk del .build-deps;


WORKDIR /code/src

COPY *py ./

CMD ["python", "run.py"]
