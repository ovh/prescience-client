FROM python:3.7.2-alpine

# Install packages
RUN apk add --no-cache libcurl
RUN apk add --no-cache make

# Needed for pycurl
ENV PYCURL_SSL_LIBRARY=openssl

RUN mkdir /prescience-client
WORKDIR /prescience-client

ADD . /prescience-client

# Install packages only needed for building, install and clean on a single layer
RUN apk add --no-cache --virtual .build-deps build-base curl-dev \
    && pip install -e . \
    && apk del --no-cache --purge .build-deps \
    && rm -rf /var/cache/apk/*

# Delete all __pycache__ files if any
RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

ARG DEFAULT_TOKEN=default_token
ARG DEFAULT_PRESCIENCE_API=https://prescience-api.ai.ovh.net
ARG DEFAULT_PRESCIENCE_WEBSOCKET=wss://prescience-websocket.ai.ovh.net
ARG DEFAULT_PRESCIENCE_ADMIN_API_URL=''

ENV PRESCIENCE_DEFAULT_TOKEN=${DEFAULT_TOKEN}
ENV PRESCIENCE_DEFAULT_API_URL=${DEFAULT_PRESCIENCE_API}
ENV PRESCIENCE_DEFAULT_WEBSOCKET_URL=${DEFAULT_PRESCIENCE_WEBSOCKET}
ENV PRESCIENCE_DEFAULT_ADMIN_API_URL=${DEFAULT_PRESCIENCE_ADMIN_API_URL}

ENTRYPOINT ["python",  "-i", "-c", "from prescience_client import prescience; prescience.config().set_project_from_env()"]
