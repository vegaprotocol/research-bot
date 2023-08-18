FROM python:3.11.4-slim

ENV POETRY_VERSION=1.2.2
ENV WALLET_VERSION=v0.71.2

ENV VEGA_WALLET_HOME=/opt/home
ENV VEGA_WALLET_PATH=/bin/vegawallet
ENV VEGA_USER_WALLET_NAME=vegamarketsim
ENV VEGA_WALLET_TOKENS_PASSPHRASE_FILE=/assets/wallet-passphrase.txt
ENV VEGA_WALLET_TOKENS_FILE=/vega_market_sim/wallet-info.json

RUN apt-get update \
    && apt-get install -y \
        git \
        unzip \
        wget \
        jq \
        make \
        rsync

RUN  pip install "poetry==$POETRY_VERSION" \
    && mkdir /research-bots

WORKDIR /research-bots

COPY . ./research-bots


# Prepare wallet and load pre generated key with known parties
RUN wget -q https://github.com/vegaprotocol/vega/releases/download/$WALLET_VERSION/vegawallet-linux-amd64.zip \
    && unzip vegawallet-linux-amd64.zip \
    && rm -f vegawallet-linux-amd64.zip \
    && mv vegawallet /bin/vegawallet \
    && chmod a+x /bin/vegawallet \
    && vegawallet software version \
    \
    && make prepare_wallet

ENTRYPOINT ["poetry", "run"]