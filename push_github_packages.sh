#!/bin/bash

if [ -f ./.env ]; then
  set -a
  source ./.env
  set +a
fi

if [ -z "${GITHUB_USERNAME}" ]; then
  echo "GITHUB_USERNAME is not set."
  exit 1
fi
if [ -z "${GITHUB_PAT}" ]; then
  echo "GITHUB_PAT is not set."
  exit 1
fi

echo R${GITHUB_PAT} | podman login ghcr.io -u ${GITHUB_USERNAME} --password-stdin

podman tag comfyui-runpod:${COMFYUI_TAG:-"latest"} ghcr.io/${GITHUB_USERNAME}/comfyui-runpod:${COMFYUI_TAG:-"latest"}
podman push ghcr.io/${GITHUB_USERNAME}/comfyui-runpod:${COMFYUI_TAG:-"latest"}
