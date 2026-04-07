#!/usr/bin/env bash
set -euo pipefail

NETWORK_NAME="${NETWORK_NAME:-temporal-lab-net}"

echo "============================================"
echo "  Temporal Worker Versioning Lab"
echo "============================================"
echo ""

# ---- Preflight ----
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Cannot reach Docker. Make sure the Docker socket is mounted."
  exit 1
fi

# ---- Python dependencies ----
echo "==> Installing Python dependencies..."
uv sync --quiet

# ---- k3d registry ----
echo "==> Setting up local container registry..."
if k3d registry list 2>/dev/null | grep -q "k3d-registry.localhost"; then
  echo "    Registry already exists, skipping."
else
  k3d registry create registry.localhost --port 5050
fi

# ---- k3d cluster on the shared network ----
echo "==> Setting up k3d cluster..."
if k3d cluster list 2>/dev/null | grep -q "temporal-lab"; then
  echo "    Cluster already exists, skipping."
else
  k3d cluster create temporal-lab \
    --network "$NETWORK_NAME" \
    --registry-use k3d-registry.localhost:5050
fi

echo "==> Waiting for cluster..."
kubectl wait --for=condition=Ready nodes --all --timeout=60s >/dev/null 2>&1

# ---- cert-manager (required by Worker Controller) ----
echo "==> Installing cert-manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml 2>&1 | tail -5
echo "    Waiting for cert-manager to be ready (this can take a minute)..."
kubectl wait --for=condition=Available deployment --all -n cert-manager --timeout=180s

# ---- Temporal dev server (in a screen session) ----
echo "==> Starting Temporal dev server (screen session: 'temporal')..."
screen -dmS temporal bash -c 'temporal server start-dev \
  --ip 0.0.0.0 \
  --dynamic-config-value "system.enableDeploymentVersions=true" \
  --dynamic-config-value "system.enableSuggestCaNOnNewTargetVersion=true" \
  --dynamic-config-value "system.enableSendTargetVersionChanged=true"'

echo "    Waiting for Temporal server..."
for i in $(seq 1 30); do
  if temporal workflow list --limit 1 >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo ""
echo "============================================"
echo "  Environment ready!"
echo "============================================"
echo ""
echo "  Temporal UI:     http://localhost:8233"
echo "  k3d cluster:     temporal-lab"
echo "  Local registry:  k3d-registry.localhost:5050"
echo ""
echo "  Temporal server logs: screen -r temporal"
echo "                        (Ctrl+A, D to detach)"
echo ""
echo "  Follow the lab to install the Temporal"
echo "  Worker Controller and deploy your first worker."
echo ""
echo "  When you exit, everything is cleaned up."
echo ""
echo "============================================"
echo ""

# Hand off to an interactive shell.
# Use bash with a trap so that when the shell exits (including SIGTERM
# from Docker when the terminal is closed), k3d is cleaned up from
# INSIDE the container where the k3d CLI is available.
exec bash --rcfile <(cat << 'BASHRC'
cleanup() {
  echo ""
  echo "==> Cleaning up k3d..."
  k3d cluster delete temporal-lab 2>/dev/null || true
  k3d registry delete registry.localhost 2>/dev/null || true
}
trap cleanup EXIT SIGTERM SIGINT
BASHRC
)
