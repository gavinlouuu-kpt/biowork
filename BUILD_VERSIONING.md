# Docker Build Versioning Guide

This guide explains how to build Docker images with proper versioning for the bioWork Label Studio project.

## Overview

The project now supports versioned Docker builds that automatically extract the version from `pyproject.toml` and tag images accordingly.

## Version Source

The version is automatically extracted from `pyproject.toml`:
```toml
[project]
version = "1.20.0"
```

## Build Methods

### 1. Versioned Build (Recommended)

Build with the version from `pyproject.toml`:

```bash
make build-versioned
```

This creates images:
- `gavinlouuu/label-studio-custom:1.20.0`
- `gavinlouuu/label-studio-custom:latest`

### 2. Custom Version Tag

Build with a specific version tag:

```bash
make build-tagged TAG=v1.21.0-beta
```

### 3. Build and Start

Build versioned image and start container:

```bash
make build-and-start-versioned
```

### 4. Environment Variable Override

Override the version using environment variables:

```bash
IMAGE_TAG=v2.0.0-rc1 ./scripts/build_docker.sh
```

### 5. Docker Compose with Versioning

Set the version in your environment or `.env` file:

```bash
export IMAGE_TAG=1.20.0
docker-compose up --build
```

Or add to `.env`:
```
IMAGE_TAG=1.20.0
```

## Image Naming

- **Default Image Name**: `gavinlouuu/label-studio-custom`
- **Override Image Name**: Set `IMAGE_NAME` environment variable
  ```bash
  IMAGE_NAME=myregistry/label-studio ./scripts/build_docker.sh
  ```

## Manual Build

If you prefer manual builds:

```bash
# Extract version and build
VERSION=$(grep -E '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
docker build -t "gavinlouuu/label-studio-custom:$VERSION" -t "gavinlouuu/label-studio-custom:latest" .
```

## Troubleshooting

### "Image already exists" error

If you get this error, the image already exists. Use one of these solutions:

1. **Force rebuild** with a different tag:
   ```bash
   IMAGE_TAG=1.20.0-$(date +%s) make build-versioned
   ```

2. **Remove existing image**:
   ```bash
   docker rmi gavinlouuu/label-studio-custom:latest
   ```

3. **Use unique tags** for development:
   ```bash
   IMAGE_TAG=dev-$(git rev-parse --short HEAD) make build-versioned
   ```

### Version not updating

Make sure to update the version in `pyproject.toml` when releasing new versions.

## CI/CD Integration

For automated builds, you can use:

```bash
# Git tag based versioning
IMAGE_TAG=$(git describe --tags --always) make build-versioned

# Timestamp based
IMAGE_TAG=$(date +%Y%m%d-%H%M%S) make build-versioned
```
