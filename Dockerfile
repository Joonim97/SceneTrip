FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    libsystemd-dev \
    pkg-config \
    python3-dev \
    build-essential \
    libgirepository1.0-dev \
    libdbus-1-dev \
    libdbus-glib-1-dev

COPY . /usr/src/app/

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

