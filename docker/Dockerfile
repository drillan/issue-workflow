FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# システムパッケージ（git, curl, jq, ca-certificates）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git curl jq ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI（公式Debianリポジトリ）
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# 非rootユーザー（UID/GIDはビルド引数で指定可能）
ARG USER_NAME=dev
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid ${USER_GID} ${USER_NAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} --create-home --shell /bin/bash ${USER_NAME}

# Claude Code インストール（非rootユーザー）
USER ${USER_NAME}
RUN curl -fsSL https://claude.ai/install.sh | bash

# 環境変数
ENV PATH="/home/${USER_NAME}/.local/bin:${PATH}"
ENV UV_PROJECT_ENVIRONMENT="/home/${USER_NAME}/.venv"
ENV UV_TOOL_BIN_DIR="/home/${USER_NAME}/.local/bin"
ENV TERM=xterm-256color
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

COPY --chown=${USER_UID}:${USER_GID} docker/entrypoint.sh /usr/local/bin/entrypoint.sh

WORKDIR /workspace
ENTRYPOINT ["entrypoint.sh"]
CMD ["bash"]
