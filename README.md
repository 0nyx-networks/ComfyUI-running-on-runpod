# ComfyUI running on runpod container

This repository provides a setup to run [ComfyUI](https://github.com/comfyanonymous/ComfyUI) on a Linux container using Podman/Docker.

## Prerequisites
- Runpod account with a GPU container
- GPU container with at NVIDIA RTX 4090

## Setup
1. Clone this repository to your local machine or directly to your Runpod container.
```bash
git clone https://github.com/m10i-0nyx/ComfyUI-running-on-runpod-container.git
cd ComfyUI-running-on-runpod-container
```

2. (Optional) Create an `env` file to specify the ComfyUI version you want to use. If not specified, it will use the default version defined in the `build.sh` script.
```bash
echo "COMFYUI_TAG=v0.3.71" > env
```

3. Build the ComfyUI container.
```bash
./build.sh
```

4. Upload AWS ECR
```bash
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)

aws ecr-public get-login-password --region us-east-1 \
  | podman login --username AWS --password-stdin public.ecr.aws/u3l2i4k1

aws ecr-public create-repository \
  --region us-east-1 \
  --repository-name comfyui-runpod

podman tag comfyui-runpod:v0.3.71 \
  public.ecr.aws/u3l2i4k1/comfyui-runpod:v0.3.71
podman push \
  public.ecr.aws/u3l2i4k1/comfyui-runpod:v0.3.71
```

## Thanks

Special thanks to everyone behind these awesome projects, without them, none of this would have been possible:

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
