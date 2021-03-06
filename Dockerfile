FROM python:3.7.2-slim

# Needed for pycurl
ENV PYCURL_SSL_LIBRARY=openssl

RUN mkdir /prescience-client
WORKDIR /prescience-client

RUN apt-get update && \
    apt-get install -y libcurl4-openssl-dev libssl-dev gcc build-essential curl

#### Jupyter lab dependencies
RUN pip install --no-cache jupyterlab ipywidgets jupyter_contrib_nbextensions && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash -  && \
    apt-get install -y nodejs && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager && \
    jupyter contrib nbextension install --user && \
    jupyter nbextension enable init_cell/main && \
    rm -rf /var/lib/apt/lists/*

ADD setup.py /prescience-client
ADD setup.cfg /prescience-client
ADD prescience /prescience-client

# Install packages only needed for building, install and clean on a single layer
RUN pip install -e .

ADD . /prescience-client

# Delete all __pycache__ files if any
RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

ARG DEFAULT_TOKEN=default_token
ARG DEFAULT_PRESCIENCE_API=https://prescience-api.ai.ovh.net
ARG DEFAULT_PRESCIENCE_WEBSOCKET=wss://prescience-websocket.ai.ovh.net
ARG DEFAULT_PRESCIENCE_ADMIN_API_URL=''
ARG DEFAULT_PRESCIENCE_SERVING_URL=https://prescience-serving.ai.ovh.net

ENV PRESCIENCE_DEFAULT_TOKEN=${DEFAULT_TOKEN}
ENV PRESCIENCE_DEFAULT_API_URL=${DEFAULT_PRESCIENCE_API}
ENV PRESCIENCE_DEFAULT_WEBSOCKET_URL=${DEFAULT_PRESCIENCE_WEBSOCKET}
ENV PRESCIENCE_DEFAULT_ADMIN_API_URL=${DEFAULT_PRESCIENCE_ADMIN_API_URL}
ENV PRESCIENCE_DEFAULT_SERVING_URL=${DEFAULT_PRESCIENCE_SERVING_URL}

ENTRYPOINT []
CMD "/bin/sh"

ENV HOME=/tmp
RUN chmod -R 777 /prescience-client