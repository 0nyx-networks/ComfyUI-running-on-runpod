#!/bin/bash

set -Eeuo pipefail

# ComfyUI tag initial value
export COMFYUI_TAG="v0.8.0"

if [ -f ./env ]; then
  set -a
  source ./env
  set +a
fi

# ComfyUIのコンテナをビルド
podman build -t comfyui-running-on-runpod:${COMFYUI_TAG} \
  --force-rm \
  --build-arg COMFYUI_TAG=${COMFYUI_TAG} \
  --device "nvidia.com/gpu=all" \
  ./services/comfyui/
