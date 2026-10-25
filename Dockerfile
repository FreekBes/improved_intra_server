FROM python:3.14-slim AS runner

RUN apt-get update && apt-get install -y \
	curl \
	libpq-dev \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY ./app/requirements.txt /app/
RUN pip install --upgrade pip && \
    if [ -f "requirements.txt" ]; then pip install -r requirements.txt; fi

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
