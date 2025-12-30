# ComfyUI running on runpod 

This repository provides a setup to run [ComfyUI](https://github.com/comfyanonymous/ComfyUI) on a Linux container using Podman/Docker.

## Prerequisites
- Runpod account with a GPU container
- GPU container with at NVIDIA RTX 4090
- Amazon Web Service(AWS) account with Elastic Container Registry (ECR) access

## Setup
1. Clone this repository to your local machine or directly to your Runpod container.
```bash
git clone https://github.com/m10i-0nyx/ComfyUI-running-on-runpod.git
cd ComfyUI-running-on-runpod
```

2. (Optional) Create an `.env` file to specify the ComfyUI version you want to use. If not specified, it will use the default version defined in the `build.sh` script.
```bash
echo "COMFYUI_TAG=v0.6.0" > .env
```

3. Build the ComfyUI container.
```bash
./build.sh
```

4. Select one of the following methods to push the container image to a container registry.

Push the container to Amazon Elastic Container Registry (ECR).
```bash
export AWS_PUBLIC_ECR_URL="public.ecr.aws/{USERNAME}/comfyui-runpod"
./push_aws_ecr.sh
```

Push the container to Github Packages Registry.
```bash
export GITHUB_USERNAME="GITHUB USERNAME"
./push_github_packages.sh
```

6. Deploy a Pod on Runpod using the pushed container image URL.

## Thanks

Special thanks to everyone behind these awesome projects, without them, none of this would have been possible:

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
