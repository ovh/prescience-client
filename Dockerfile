FROM python:3.7.2-alpine

# Install packages
RUN apk add --no-cache libcurl
RUN apk add --no-cache make

# Needed for pycurl
ENV PYCURL_SSL_LIBRARY=openssl

RUN mkdir /prescience-client
WORKDIR /prescience-client

ADD requirements.txt /prescience-client

# Install packages only needed for building, install and clean on a single layer
RUN apk add --no-cache --virtual .build-deps build-base curl-dev \
    && pip install -r requirements.txt \
    && apk del --no-cache --purge .build-deps \
    && rm -rf /var/cache/apk/*

ADD . /prescience-client

# Delete all __pycache__ files if any
RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

ARG DEFAULT_TOKEN=token

ENV PRESCIENCE_DEFAULT_TOKEN=${DEFAULT_TOKEN}

ENTRYPOINT ["python",  "-i", "-c", "from prescience_client import prescience; prescience.config().set_project_from_env()"]
