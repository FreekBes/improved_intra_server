FROM python:3.10-slim as runner

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
RUN mkdir -p /app/logs

ENV DEBUG=False

CMD ["gunicorn", "-w", "1", "--bind", "0.0.0.0:8000", "--access-logfile", "logs/access.log", "--error-logfile", "logs/error.log", "wsgi:app"]
