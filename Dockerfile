FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x /app/entrypoint.sh && chown -R app:app /app

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python /app/scripts/healthcheck.py || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
