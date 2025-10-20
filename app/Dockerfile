FROM python:3.14-slim

WORKDIR /app

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

COPY requirements.txt .

COPY --chown=appuser:appgroup src/ ./src/

USER appuser

ENTRYPOINT ["python3"]
CMD ["src/main.py"]