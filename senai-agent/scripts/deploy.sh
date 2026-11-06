#!/bin/bash
# =============================================================================
# scripts/deploy.sh
# Deploy do SENAI Empresa Assistant no IBM Cloud Code Engine
#
# COMO USAR:
#   1. Preencha todas as variáveis no arquivo .env (copie de .env.example)
#   2. Execute: bash scripts/deploy.sh
# =============================================================================

set -euo pipefail

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "❌ Arquivo .env não encontrado. Copie .env.example para .env e preencha."
  exit 1
fi

: "${IBM_CLOUD_API_KEY:?}"
: "${IBM_CLOUD_REGION:?}"
: "${IBM_CLOUD_RESOURCE_GROUP:?}"
: "${IBM_CLOUD_REGISTRY_NAMESPACE:?}"
: "${CODE_ENGINE_PROJECT:?}"

APP_NAME="senai-empresa-assistant"
IMAGE_TAG="${IBM_CLOUD_REGION}.icr.io/${IBM_CLOUD_REGISTRY_NAMESPACE}/${APP_NAME}:latest"

echo "Deploy: $APP_NAME → $IMAGE_TAG"

ibmcloud login --apikey "$IBM_CLOUD_API_KEY" -r "$IBM_CLOUD_REGION" -g "$IBM_CLOUD_RESOURCE_GROUP" --quiet
ibmcloud cr login
docker build -t "$IMAGE_TAG" .
docker push "$IMAGE_TAG"

if ibmcloud ce project list | grep -q "$CODE_ENGINE_PROJECT"; then
  ibmcloud ce project select --name "$CODE_ENGINE_PROJECT"
else
  ibmcloud ce project create --name "$CODE_ENGINE_PROJECT"
fi

ibmcloud ce secret delete --name senai-agent-secrets --force 2>/dev/null || true
ibmcloud ce secret create --name senai-agent-secrets \
  --from-literal ORCHESTRATE_API_KEY="$ORCHESTRATE_API_KEY" \
  --from-literal ORCHESTRATE_INSTANCE_URL="$ORCHESTRATE_INSTANCE_URL"

if ibmcloud ce app list | grep -q "$APP_NAME"; then
  ibmcloud ce app update --name "$APP_NAME" --image "$IMAGE_TAG" \
    --env-from-secret senai-agent-secrets --min-scale 0 --max-scale 5 --memory 2G --cpu 0.5
else
  ibmcloud ce app create --name "$APP_NAME" --image "$IMAGE_TAG" \
    --env-from-secret senai-agent-secrets --min-scale 0 --max-scale 5 --memory 2G --cpu 0.5 --port 8080
fi

APP_URL=$(ibmcloud ce app get --name "$APP_NAME" --output json | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status',{}).get('url','N/A'))")

echo "✅ Deploy concluído! URL: $APP_URL"
