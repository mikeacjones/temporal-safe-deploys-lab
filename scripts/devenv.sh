#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONTAINER_NAME="temporal-lab-devenv"
IMAGE_NAME="temporal-lab-devenv"
NETWORK_NAME="temporal-lab-net"

cleanup() {
  echo ""
  echo "==> Cleaning up..."
  # Kill all k3d containers for our cluster (server, serverlb, tools, registry)
  docker rm -f $(docker ps -a --filter "name=k3d-temporal-lab" -q) 2>/dev/null || true
  docker rm -f $(docker ps -a --filter "name=k3d-registry.localhost" -q) 2>/dev/null || true
  # Remove k3d volumes
  docker volume rm $(docker volume ls --filter "name=k3d-temporal-lab" -q) 2>/dev/null || true
  # Remove the shared network
  docker network rm "$NETWORK_NAME" 2>/dev/null || true
  echo "    Done."
}

# Always clean up, even on ctrl+c or crash
trap cleanup EXIT

# Find Docker socket
if [ -S "/var/run/docker.sock" ]; then
  DOCKER_SOCK="/var/run/docker.sock"
elif [ -S "$HOME/.docker/run/docker.sock" ]; then
  DOCKER_SOCK="$HOME/.docker/run/docker.sock"
else
  echo "ERROR: Cannot find Docker socket. Is Docker running?"
  exit 1
fi

# Create shared network
docker network create "$NETWORK_NAME" 2>/dev/null || true

# Build the dev environment image
echo "==> Building dev environment..."
docker build -t "$IMAGE_NAME" -f "$PROJECT_DIR/Dockerfile.devenv" "$PROJECT_DIR"

# Run the container. Entrypoint handles k3d/temporal setup.
docker run -it --rm \
  --name "$CONTAINER_NAME" \
  --network "$NETWORK_NAME" \
  -p 7233:7233 \
  -p 8233:8233 \
  -v "$DOCKER_SOCK":/var/run/docker.sock \
  -v "$PROJECT_DIR":/app \
  -e NETWORK_NAME="$NETWORK_NAME" \
  "$IMAGE_NAME" || true

# trap EXIT handles cleanup automatically
