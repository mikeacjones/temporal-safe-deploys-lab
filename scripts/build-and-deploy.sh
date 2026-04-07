#!/usr/bin/env bash
set -euo pipefail

BUILD_ID="${1:?Usage: build-and-deploy.sh <BUILD_ID> [--versioned]}"
VERSIONED=false
if [[ "${2:-}" == "--versioned" ]]; then
  VERSIONED=true
fi

IMAGE="k3d-registry.localhost:5050/research-agent:${BUILD_ID}"

echo "==> Building image: ${IMAGE}"
docker build -t "${IMAGE}" .

echo "==> Pushing to local registry..."
docker push "${IMAGE}"

if [ "$VERSIONED" = true ]; then
  echo "==> Deploying with Worker Controller (build ID: ${BUILD_ID})..."
  helm upgrade --install research-agent ./charts/worker \
    --set "image.tag=${BUILD_ID}" \
    --namespace default

  echo ""
  echo "Done. Check status with:"
  echo "  kubectl get temporalworkerdeployments -n default"
  echo "  kubectl get pods -n default"
else
  echo "==> Deploying as standard Deployment (build ID: ${BUILD_ID})..."
  helm upgrade --install research-agent ./charts/worker-simple \
    --set "image.tag=${BUILD_ID}" \
    --namespace default

  echo ""
  echo "Done. Check status with:"
  echo "  kubectl get deployments -n default"
  echo "  kubectl get pods -n default"
fi
