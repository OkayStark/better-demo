#!/usr/bin/env bash
set -e
IMAGE="$1"
CONTAINER_NAME="better-demo"

# stop + remove old container if exists
if docker ps -a --format '{{.Names}}' | grep -q "${CONTAINER_NAME}"; then
  docker rm -f ${CONTAINER_NAME} || true
fi

# pull latest and run
docker pull ${IMAGE}
docker run -d --name ${CONTAINER_NAME} -p 80:5000 --restart unless-stopped \
  --env-file /home/.env \
  -e DATADOG_API_KEY="${DATADOG_API_KEY:-}" \
  -e SERVICE_NAME="better-demo" \
  ${IMAGE}

# print status
sleep 2
docker ps --filter "name=${CONTAINER_NAME}"
