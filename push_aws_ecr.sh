#!/bin/bash

export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
export AWS_PUBLIC_ECR_URL=${AWS_PUBLIC_ECR_URL:-'public.ecr.aws/m10i/comfyui-running-on-runpod'}

# ComfyUI tag initial value
export COMFYUI_TAG="v0.8.0"

if [ -f ./env ]; then
  set -a
  source ./env
  set +a
fi

aws ecr-public get-login-password --region us-east-1 \
  | podman login --username AWS --password-stdin ${AWS_PUBLIC_ECR_URL}

aws ecr-public create-repository \
  --region us-east-1 \
  --repository-name comfyui-running-on-runpod

podman tag comfyui-running-on-runpod:${COMFYUI_TAG:-"latest"} ${AWS_PUBLIC_ECR_URL}:${COMFYUI_TAG:-"latest"}
podman push ${AWS_PUBLIC_ECR_URL}:${COMFYUI_TAG:-"latest"}
podman tag ${AWS_PUBLIC_ECR_URL}:${COMFYUI_TAG:-"latest"} ${AWS_PUBLIC_ECR_URL}:latest
podman push ${AWS_PUBLIC_ECR_URL}:latest
podman image rm ${AWS_PUBLIC_ECR_URL}:latest
podman image rm ${AWS_PUBLIC_ECR_URL}:${COMFYUI_TAG:-"latest"}
