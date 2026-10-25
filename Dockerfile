# Build stage: compiles psycopg2 into a virtualenv. None of the toolchain this
# needs ends up in the image that actually runs.
FROM python:3.14-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
	gcc \
	build-essential \
	libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY ./app/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt


# Runtime stage
FROM python:3.14-slim AS runner

# libpq5 is the runtime half of libpq-dev, which psycopg2 links against;
# curl answers the container healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends \
	curl \
	libpq5 \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PATH="/app/venv/bin:$PATH"

COPY --from=builder /app/venv /app/venv

COPY ./app /app/
RUN chmod +x /app/entrypoint.sh
# Public, non-secret defaults are version-controlled and ride along with the
# image; .private.env supplies only secrets and per-deployment overrides.
# .private.env is of course not copied into the image. Mount it yourself.
COPY .public.env /app/.public.env
# The application serves its own static files, so they belong in the image.
# User uploads under static/banners are bind-mounted from data/ instead.
COPY ./static /app/static
RUN mkdir -p /app/logs /app/static/banners

ENV DEBUG=False

CMD ["./entrypoint.sh"]
