ARG NANOBOT_REPO=https://github.com/HKUDS/nanobot.git
ARG NANOBOT_REF=main

# =============================================================================
# Builder stage
# =============================================================================
FROM python:3.11-slim AS builder

ARG NANOBOT_REPO
ARG NANOBOT_REF

RUN apt-get update && \
    apt-get install -y git curl nodejs npm && \
    rm -rf /var/lib/apt/lists/*

RUN pip install uv

RUN git clone --depth 1 --branch ${NANOBOT_REF} ${NANOBOT_REPO} /opt/nanobot

RUN cd /opt/nanobot && uv pip install --system -e .

RUN cd /opt/nanobot/bridge && npm install && npm run build

# =============================================================================
# Runtime stage
# =============================================================================
FROM python:3.11-slim

# Install apt baseline packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git jq tmux curl ca-certificates gnupg xz-utils && \
    rm -rf /var/lib/apt/lists/*

# Install GitHub CLI (gh) via official apt repository
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y --no-install-recommends gh && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js 20 via NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Nix via DeterminateSystems installer
RUN curl --proto '=https' --tlsv1.2 -sSf -L \
    https://install.determinate.systems/nix | sh -s -- install linux \
    --extra-conf "sandbox = false" --init none --no-confirm
ENV PATH="${PATH}:/nix/var/nix/profiles/default/bin"
ENV XDG_CACHE_HOME="/tmp/.cache"

# Copy nanobot installation from builder
COPY --from=builder /opt/nanobot /opt/nanobot
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/nanobot /usr/local/bin/nanobot

# Install channels dependencies (e.g. discord)
RUN cd /opt/nanobot && pip install -e ".[discord]"

# Copy distro files
COPY scripts/ /opt/nanobot-nix/scripts/
COPY skills/ /opt/nanobot-nix/skills/
RUN chmod +x /opt/nanobot-nix/scripts/*.sh

WORKDIR /opt/nanobot-nix

ENTRYPOINT ["/opt/nanobot-nix/scripts/entrypoint.sh"]
CMD []
