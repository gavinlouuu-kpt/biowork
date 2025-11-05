SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"

# Extract version from pyproject.toml
VERSION=$(grep -E '^version = ' "${PROJECT_ROOT}/pyproject.toml" | head -1 | sed 's/version = "\(.*\)"/\1/')

# Use IMAGE_TAG environment variable or default to version
IMAGE_TAG=${IMAGE_TAG:-${VERSION}}
IMAGE_NAME=${IMAGE_NAME:-gavinlouuu/label-studio-custom}

echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"

if bash ${SCRIPT_DIR}/../deploy/prebuild.sh; then
  docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" -t "${IMAGE_NAME}:latest" "${PROJECT_ROOT}"
fi