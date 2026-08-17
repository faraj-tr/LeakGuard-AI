FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

ENV LEAKGUARD_CONTAINER_MODE=1
ENV LEAKGUARD_API_SCAN_ROOT=/workspace
ENV LEAKGUARD_MODEL_HOME=/models
ENV LEAKGUARD_API_URL=http://127.0.0.1:8000

WORKDIR /app

RUN groupadd --system leakguard     && useradd         --system         --gid leakguard         --create-home         --home-dir /home/leakguard         leakguard

COPY pyproject.toml ./
COPY src ./src

RUN python -m pip install .

RUN mkdir -p /workspace /models     && chown -R         leakguard:leakguard         /workspace         /models         /home/leakguard

USER leakguard

EXPOSE 8501

HEALTHCHECK     --interval=30s     --timeout=5s     --start-period=20s     --retries=3     CMD ["python", "-c", "import json, urllib.request; r = urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3); d = json.load(r); raise SystemExit(0 if r.status == 200 and d.get('status') == 'ok' else 1)"]

CMD ["leakguard-stack"]
