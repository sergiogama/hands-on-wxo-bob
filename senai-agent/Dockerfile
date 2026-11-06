FROM python:3.11-slim

LABEL maintainer="SENAI Dev Team"
LABEL description="SENAI Empresa Assistant — watsonx Orchestrate Agent"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/ ./agents/
COPY mcp_server/ ./mcp_server/

RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8080
CMD ["python", "-m", "agents.senai_empresa_agent"]
