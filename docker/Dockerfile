FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    && curl -Ls https://astral.sh/uv/install.sh | sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# uv environment variables
ENV PATH="/root/.local/bin:$PATH"
ENV UV_LINK_MODE=copy

WORKDIR /app
