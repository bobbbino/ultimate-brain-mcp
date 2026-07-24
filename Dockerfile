# Build stage: install the locked dependency set + the package into a venv.
# The uv python3.13 images derive from the official python:3.13-slim-bookworm
# image, so the venv's interpreter path resolves identically in the runtime
# stage below.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS build

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies first, project second, so the (much larger) dependency layer
# caches across source-only changes.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY README.md LICENSE ./
COPY src/ src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Runtime stage: plain Python, no uv, non-root.
FROM python:3.14-slim-bookworm

RUN useradd --system --uid 10001 --create-home ub

# Same path as the build stage so the venv's entry-point shebangs stay valid.
COPY --from=build --chown=ub:ub /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Container default is HTTP serving; override UB_TRANSPORT=stdio (with
# `docker run -i`) for stdio clients. 0.0.0.0 because in-container localhost
# is unreachable from outside.
ENV UB_TRANSPORT=streamable-http \
    UB_HOST=0.0.0.0 \
    UB_PORT=8000
EXPOSE 8000

USER ub
ENTRYPOINT ["ultimate-brain-mcp"]
