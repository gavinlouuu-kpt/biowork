# Task: Docker ML Backend Configuration

## Status: COMPLETED

## Objective
Configure Label Studio Docker deployment to use environment variables for ML backend URL management, ensuring proper Docker networking and BASE_DATA_DIR configuration.

## Problem Identified
The `.env` file approach documented earlier works for local development but not for Docker deployments because:
1. The `.env` file in `data/` directory is not included in the Docker image
2. Docker containers should use environment variables set in `docker-compose.yml`
3. Docker networking requires using service names instead of `localhost`

## Solution Implemented

### 1. Updated docker-compose.yml
**File**: `/Users/reading/Developer/label-studio-custom/docker-compose.yml`

Added environment variables to the `app` service:
```yaml
environment:
  # Existing variables
  - DJANGO_DB=default
  - POSTGRE_NAME=postgres
  - POSTGRE_USER=postgres
  - POSTGRE_PASSWORD=postgres
  - POSTGRE_PORT=5432
  - POSTGRE_HOST=db
  - LABEL_STUDIO_HOST=${LABEL_STUDIO_HOST:-http://localhost:8080}
  - JSON_LOG=1
  # NEW: ML Backend Configuration
  - ADD_DEFAULT_ML_BACKENDS=true
  - DEFAULT_ML_BACKEND_URL=http://sam-ml-backend:9090
  - DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
  # NEW: Base Data Directory (inside container)
  - BASE_DATA_DIR=/label-studio/data
```

### 2. Key Configuration Decisions

#### ML Backend URL
- **Docker**: `http://sam-ml-backend:9090` (uses Docker service name)
- **Local Dev**: `http://localhost:9090` (uses localhost)

The service name `sam-ml-backend` comes from the container name in the SAM ML backend's docker-compose.yml.

#### BASE_DATA_DIR
- **Docker**: `/label-studio/data` (path inside container)
- **Local Dev**: `/Users/reading/Developer/label-studio-custom/data` (absolute host path)

#### Network Configuration
Both services must be on the same Docker network:
- Label Studio creates: `label-studio-network`
- SAM ML backend joins: `label-studio-network` (external: true)

## Configuration Summary

### For Docker Deployment (Production/Testing)
**Location**: `docker-compose.yml` environment section
```yaml
environment:
  - ADD_DEFAULT_ML_BACKENDS=true
  - DEFAULT_ML_BACKEND_URL=http://sam-ml-backend:9090
  - DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
  - BASE_DATA_DIR=/label-studio/data
```

### For Local Development (Non-Docker)
**Location**: `data/.env`
```env
ADD_DEFAULT_ML_BACKENDS=true
DEFAULT_ML_BACKEND_URL=http://localhost:9090
DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
BASE_DATA_DIR=/Users/reading/Developer/label-studio-custom/data
```

## Documentation Created

1. **`knowledge_map/DOCKER_ML_BACKEND_CONFIGURATION.md`**
   - Complete guide for Docker deployments
   - Explains Docker networking for ML backends
   - Troubleshooting guide for common issues
   - Best practices for production

2. **`knowledge_map/ML_BACKEND_CONFIGURATION.md`** (previously created)
   - Guide for local development (non-Docker)
   - Explains .env file approach

3. **`knowledge_map/ENV_TEMPLATE_REFERENCE.md`** (previously created)
   - Complete reference for all environment variables
   - Includes both Docker and non-Docker examples

## Testing Instructions

### 1. Restart Label Studio Container
```bash
cd /Users/reading/Developer/label-studio-custom
docker-compose restart app
```

### 2. Verify Environment Variables
```bash
docker exec label-studio-app env | grep -E "ML_BACKEND|BASE_DATA"
```

Expected output:
```
ADD_DEFAULT_ML_BACKENDS=true
DEFAULT_ML_BACKEND_URL=http://sam-ml-backend:9090
DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
BASE_DATA_DIR=/label-studio/data
```

### 3. Test Network Connectivity
```bash
docker exec label-studio-app curl -I http://sam-ml-backend:9090/health
```

Expected: HTTP 200 OK

### 4. Create New Project
1. Access Label Studio at http://localhost:8080
2. Create a new project
3. Go to Settings > Machine Learning
4. Verify "SAM Interactive Segmentation" is automatically connected

### 5. Check Logs
```bash
docker logs label-studio-app | grep -i "ml backend"
```

Expected log messages:
- "Auto-connected ML backend SAM Interactive Segmentation..."

## Files Modified

1. `/Users/reading/Developer/label-studio-custom/docker-compose.yml`
   - Added ML backend environment variables
   - Added BASE_DATA_DIR configuration

## Documentation Files Created

1. `/Users/reading/Developer/label-studio-custom/knowledge_map/DOCKER_ML_BACKEND_CONFIGURATION.md`
2. `/Users/reading/Developer/label-studio-custom/knowledge_map/task/docker-ml-backend-configuration.md` (this file)

## Related Tasks

- Original task: `knowledge_map/task/ml-backend-env-configuration.md`
- That task documented the .env approach for local development
- This task extends it for Docker deployments

## Architecture

```
┌─────────────────────────────────────────┐
│   label-studio-network (Docker Network) │
│                                           │
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ label-studio-app│  │ sam-ml-backend│ │
│  │ (port 8000)     │◄─┤ (port 9090)   │ │
│  │                 │  │               │ │
│  │ Environment:    │  │ Accessed via: │ │
│  │ DEFAULT_ML_     │  │ service name  │ │
│  │ BACKEND_URL=    │  │ not localhost │ │
│  │ http://sam-ml-  │  │               │ │
│  │ backend:9090    │  │               │ │
│  └─────────────────┘  └───────────────┘ │
│                                           │
│  ┌─────────────────┐                     │
│  │ label-studio-db │                     │
│  │ (PostgreSQL)    │                     │
│  └─────────────────┘                     │
└─────────────────────────────────────────┘
         │
         │ Exposed to host
         ▼
    localhost:8080 (nginx)
```

## Success Criteria

- [x] docker-compose.yml updated with ML backend environment variables
- [x] BASE_DATA_DIR configured for Docker container path
- [x] ML backend URL uses Docker service name (not localhost)
- [x] Comprehensive Docker documentation created
- [x] Testing instructions documented
- [ ] Configuration tested (requires container restart)
- [ ] New project created to verify auto-connection (requires testing)

## Next Steps

1. **Restart Label Studio container** to apply new environment variables:
   ```bash
   cd /Users/reading/Developer/label-studio-custom
   docker-compose restart app
   ```

2. **Verify environment variables** are loaded:
   ```bash
   docker exec label-studio-app env | grep ML_BACKEND
   ```

3. **Create a test project** and verify ML backend auto-connection

4. **Check logs** for successful auto-connection messages

## Important Notes

### Docker vs Local Development

| Aspect | Docker | Local Development |
|--------|--------|-------------------|
| Config Location | `docker-compose.yml` | `data/.env` |
| ML Backend URL | `http://sam-ml-backend:9090` | `http://localhost:9090` |
| BASE_DATA_DIR | `/label-studio/data` | `/Users/.../data` |
| Network | `label-studio-network` | Host network |

### Why This Approach?

1. **Separation of Concerns**: Docker config in docker-compose.yml, local config in .env
2. **Docker Best Practice**: Environment variables in compose file are visible and version-controlled
3. **Network Compatibility**: Docker service names work within Docker networks
4. **Path Correctness**: Container paths match volume mounts
5. **Flexibility**: Easy to override via .env file or environment variables

### Alternative: .env File for Docker Compose

You could also create a `.env` file at the project root (not in data/) and reference variables:

```yaml
environment:
  - ADD_DEFAULT_ML_BACKENDS=${ADD_DEFAULT_ML_BACKENDS:-false}
  - DEFAULT_ML_BACKEND_URL=${DEFAULT_ML_BACKEND_URL}
```

But the direct approach (current implementation) is clearer and more explicit.

## Troubleshooting Reference

See `knowledge_map/DOCKER_ML_BACKEND_CONFIGURATION.md` for detailed troubleshooting guide including:
- Network connectivity issues
- Service name resolution
- Environment variable verification
- Log analysis
- Common error messages and solutions

