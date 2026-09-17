# local/Dockerfile — the Tilt / kind inner loop
#
# Layout-agnostic on purpose: this overlay retrofits an EXISTING application, so it copies the whole
# repo and runs the application's OWN build command rather than assuming a module name, a crate, a
# src/ layout or an output path. `build_command` and `runtime_artifact` are answers; their defaults
# match what this language's p6m service archetype produces, so a greenfield-shaped repo needs
# neither.

FROM python:3.12-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv
COPY . .
RUN uv pip install --system --no-cache .

FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin/test-app /usr/local/bin/test-app
USER appuser
EXPOSE 8080 8081
ENTRYPOINT ["test-app"]
