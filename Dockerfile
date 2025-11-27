FROM ubuntu:noble

RUN apt update -y
RUN apt install curl wget xz-utils -y

RUN set -eux; \
    LATEST_VERSION=$(curl --silent -I https://github.com/qupath/qupath/releases/latest/ \
        | grep location \
        | awk -F/ '{print $NF}' \
        | tr -d '\r'); \
    echo "Latest version: $LATEST_VERSION"; \
    wget "https://github.com/qupath/qupath/releases/download/${LATEST_VERSION}/QuPath-${LATEST_VERSION}-Linux.tar.xz"; \
    tar xvf "QuPath-${LATEST_VERSION}-Linux.tar.xz"; \
    rm "QuPath-${LATEST_VERSION}-Linux.tar.xz"; \
    chmod a+x /QuPath/bin/QuPath; \
    sed -i 's/MaxRAMPercentage=50/MaxRAMPercentage=90/' /QuPath/lib/app/QuPath.cfg

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY cli/.python-version /cli/.python-version
COPY cli/pyproject.toml /cli/pyproject.toml
COPY cli/uv.lock /cli/uv.lock
WORKDIR /cli
RUN uv sync

COPY extensions /scripts/userdir/extensions

COPY scripts/prefs.groovy /scripts/prefs.groovy
RUN /QuPath/bin/QuPath script /scripts/prefs.groovy

COPY scripts/segment.groovy /scripts/segment.groovy
COPY scripts/models/stardist_model_1_channel.pb /scripts/models/stardist_model_1_channel.pb

COPY cli/main.py /cli/main.py

ENTRYPOINT ["uv", "run", "/cli/main.py"]
