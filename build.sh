#!/bin/bash

set -Eeuo pipefail

if [ -f env ]; then
  set -a
  source ./env
  set +a
fi

# ComfyUIのコンテナをビルド
podman build -t comfyui-runpod:${COMFYUI_TAG} \
  --force-rm \
  --build-arg COMFYUI_TAG=${COMFYUI_TAG} \
  --device "nvidia.com/gpu=all" \
  ./services/comfyui/
