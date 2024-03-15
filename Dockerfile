FROM python:3.11.8

ENV POETRY_VERSION=1.2.2
ENV WALLET_VERSION=v0.71.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends\
        git \
        unzip \
        wget \
        jq \
        make \
        gcc \
        build-essential \
        libpython3.11-dev \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

RUN  pip install "poetry==$POETRY_VERSION" \
    pip install cython \
    && mkdir /research-bots

WORKDIR /research-bots

COPY . .

# Prepare wallet and load pre generated key with known parties
RUN make prepare_bots_prod

ENTRYPOINT ["make"]