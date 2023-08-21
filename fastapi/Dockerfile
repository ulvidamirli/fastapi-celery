FROM python:3.11-slim-buster

# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Allow statements and log messages to immediately appear
ENV PYTHONUNBUFFERED 1
# Disable a pip version check to reduce run-time & log-spam
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
# Cache is useless in docker image, so disable to reduce image size
ENV PIP_NO_CACHE_DIR 1

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
 
COPY ./app /code/app
