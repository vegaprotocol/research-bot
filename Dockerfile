FROM python:3.11.4-slim

ENV POETRY_VERSION=1.2.2
ENV WALLET_VERSION=v0.71.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends\
        git \
        unzip \
        wget \
        jq \
        make \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

RUN  pip install "poetry==$POETRY_VERSION" \
    && mkdir /research-bots

WORKDIR /research-bots

COPY . .

RUN make prepare_bots_prod

ENTRYPOINT ["make"]