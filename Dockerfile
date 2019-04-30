FROM python:stretch

RUN mkdir /src
WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /src 

RUN pip install -r requirements.txt
