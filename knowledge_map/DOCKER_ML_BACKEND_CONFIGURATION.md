# Docker ML Backend Configuration

## Overview

For Docker deployments, environment variables should be configured directly in the `docker-compose.yml` file rather than using a `.env` file inside the data directory. This is because:

1. The `.env` file in the data directory is loaded after the container starts
2. Docker environment variables are set before the application starts
3. Docker Compose provides better environment variable management for containers

## Configuration Approaches

### 1. Local Development (Non-Docker)
For local development without Docker, use the `.env` file approach:
- Location: `/path/to/label-studio-custom/data/.env`
- See: `knowledge_map/ML_BACKEND_CONFIGURATION.md`

### 2. Docker Deployment (Recommended)
For Docker deployments, use environment variables in `docker-compose.yml`:
- Location: `/path/to/label-studio-custom/docker-compose.yml`
- Method: Add environment variables to the `app` service

## Docker Compose Configuration

### Updated docker-compose.yml

The `app` service should include ML backend environment variables:

```yaml
  app:
    stdin_open: true
    tty: true
    build:
      context: .
      dockerfile: Dockerfile
    image: label-studio-custom:latest
    container_name: label-studio-app
    restart: unless-stopped
    expose:
      - "8000"
    depends_on:
      - db
    environment:
      - DJANGO_DB=default
      - POSTGRE_NAME=postgres
      - POSTGRE_USER=postgres
      - POSTGRE_PASSWORD=postgres
      - POSTGRE_PORT=5432
      - POSTGRE_HOST=db
      - LABEL_STUDIO_HOST=${LABEL_STUDIO_HOST:-http://localhost:8080}
      - JSON_LOG=1
      # ML Backend Configuration
      - ADD_DEFAULT_ML_BACKENDS=true
      - DEFAULT_ML_BACKEND_URL=http://sam-ml-backend:9090
      - DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
      # Base Data Directory (inside container)
      - BASE_DATA_DIR=/label-studio/data
    volumes:
      - ./mydata:/label-studio/data:rw
    command: label-studio-uwsgi
    networks:
      - label-studio-network
```

## Key Configuration Points

### 1. ML Backend URL for Docker
**Important**: Use the Docker service name, not `localhost`:
- ✅ Correct: `DEFAULT_ML_BACKEND_URL=http://sam-ml-backend:9090`
- ❌ Wrong: `DEFAULT_ML_BACKEND_URL=http://localhost:9090`

The container name from your SAM ML backend (`sam-ml-backend`) becomes the hostname within the Docker network.

### 2. Network Configuration
Both services must be on the same Docker network:

```yaml
# In label-studio-custom/docker-compose.yml
networks:
  label-studio-network:
    name: label-studio-network
    driver: bridge

# In ls-ml-backend-SAM/docker-compose.yml
networks:
  label-studio-network:
    external: true
```

### 3. BASE_DATA_DIR for Docker
Inside the container, the data directory is mounted at `/label-studio/data`:
```yaml
environment:
  - BASE_DATA_DIR=/label-studio/data
volumes:
  - ./mydata:/label-studio/data:rw
```

This means:
- Host path: `./mydata`
- Container path: `/label-studio/data`
- Environment variable: `BASE_DATA_DIR=/label-studio/data`

## Alternative: Using .env File with Docker Compose

You can also create a `.env` file at the project root (not in data/) for Docker Compose:

**File: `/Users/reading/Developer/label-studio-custom/.env`**
```env
# Docker Compose environment variables
LABEL_STUDIO_HOST=http://localhost:8080
POSTGRES_DATA_DIR=./postgres-data

# Label Studio environment variables
ADD_DEFAULT_ML_BACKENDS=true
DEFAULT_ML_BACKEND_URL=http://sam-ml-backend:9090
DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
BASE_DATA_DIR=/label-studio/data
```

Then reference them in docker-compose.yml with `${VARIABLE_NAME}`:

```yaml
  app:
    environment:
      - ADD_DEFAULT_ML_BACKENDS=${ADD_DEFAULT_ML_BACKENDS:-false}
      - DEFAULT_ML_BACKEND_URL=${DEFAULT_ML_BACKEND_URL}
      - DEFAULT_ML_BACKEND_TITLE=${DEFAULT_ML_BACKEND_TITLE:-Default ML Backend}
      - BASE_DATA_DIR=${BASE_DATA_DIR:-/label-studio/data}
```

## Complete Docker Setup

### 1. Label Studio docker-compose.yml

Located at: `/Users/reading/Developer/label-studio-custom/docker-compose.yml`

Key settings:
- Network: `label-studio-network` (created)
- ML Backend URL: `http://sam-ml-backend:9090` (Docker service name)
- Data volume: `./mydata:/label-studio/data:rw`

### 2. SAM ML Backend docker-compose.yml

Located at: `/Users/reading/Developer/ls-ml-backend-SAM/docker-compose.yml`

Key settings:
- Container name: `sam-ml-backend`
- Network: `label-studio-network` (external)
- Port: `9090:9090`
- Uses `.env` file for its own configuration

### 3. Start Order

```bash
# 1. Start Label Studio (creates network)
cd /Users/reading/Developer/label-studio-custom
docker-compose up -d

# 2. Start SAM ML Backend (joins network)
cd /Users/reading/Developer/ls-ml-backend-SAM
docker-compose up -d
```

## Environment Variables Reference

### ML Backend Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `ADD_DEFAULT_ML_BACKENDS` | `true` | Enable auto-connection |
| `DEFAULT_ML_BACKEND_URL` | `http://sam-ml-backend:9090` | ML backend URL (Docker service name) |
| `DEFAULT_ML_BACKEND_TITLE` | `SAM Interactive Segmentation` | Display name |

### Path Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `BASE_DATA_DIR` | `/label-studio/data` | Data directory inside container |

### Database Variables (PostgreSQL)

| Variable | Value | Description |
|----------|-------|-------------|
| `DJANGO_DB` | `default` | Database type (postgresql) |
| `POSTGRE_HOST` | `db` | Docker service name |
| `POSTGRE_PORT` | `5432` | PostgreSQL port |
| `POSTGRE_NAME` | `postgres` | Database name |
| `POSTGRE_USER` | `postgres` | Database user |
| `POSTGRE_PASSWORD` | `postgres` | Database password |

## Verifying Configuration

### 1. Check Environment Variables in Container

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

### 2. Check Network Connectivity

```bash
# Test if Label Studio can reach SAM backend
docker exec label-studio-app curl -I http://sam-ml-backend:9090/health
```

Expected: HTTP 200 OK response

### 3. Check Label Studio Logs

```bash
docker logs label-studio-app | grep -i "ml backend"
```

Expected log messages:
- "Auto-connected ML backend..."
- "SAM Interactive Segmentation"

## Troubleshooting

### Issue: ML Backend Not Connecting

**Symptoms:**
- New projects don't have ML backend automatically connected
- No "Auto-connected" messages in logs

**Solutions:**
1. Verify environment variables are set:
   ```bash
   docker exec label-studio-app env | grep ML_BACKEND
   ```

2. Check SAM backend is running:
   ```bash
   docker ps | grep sam-ml-backend
   ```

3. Test network connectivity:
   ```bash
   docker exec label-studio-app ping -c 3 sam-ml-backend
   ```

4. Restart Label Studio:
   ```bash
   docker-compose restart app
   ```

### Issue: Wrong BASE_DATA_DIR

**Symptoms:**
- Database or media files not found
- Permission errors

**Solutions:**
1. Verify volume mount:
   ```bash
   docker inspect label-studio-app | grep -A 10 Mounts
   ```

2. Check BASE_DATA_DIR matches mount point:
   ```bash
   docker exec label-studio-app env | grep BASE_DATA_DIR
   # Should show: BASE_DATA_DIR=/label-studio/data
   ```

### Issue: Can't Connect via localhost:9090

**Problem**: Using `localhost:9090` instead of Docker service name

**Solution**: Update docker-compose.yml:
```yaml
- DEFAULT_ML_BACKEND_URL=http://sam-ml-backend:9090  # NOT localhost
```

### Issue: Network Not Found

**Symptoms:**
```
ERROR: Network label-studio-network declared as external, but could not be found
```

**Solution**: Start Label Studio first (creates network):
```bash
cd /Users/reading/Developer/label-studio-custom
docker-compose up -d
```

## Best Practices

1. **Use Docker Service Names**: Always use container/service names for inter-container communication
2. **Separate Networks**: Keep Label Studio and ML backend on the same network
3. **Environment Variables**: Define all configuration in docker-compose.yml for visibility
4. **Volume Mounts**: Ensure data directories are properly mounted and writable
5. **Health Checks**: Both services should have health checks configured
6. **Restart Policies**: Use `restart: unless-stopped` for production

## Production Considerations

For production deployments:

1. **Use Secrets**: Store sensitive data in Docker secrets or external secret managers
2. **Resource Limits**: Set memory and CPU limits
3. **Persistent Storage**: Use named volumes or external storage for data
4. **Monitoring**: Add logging drivers and monitoring tools
5. **Backup**: Regular backups of data volumes and database

Example production configuration:
```yaml
  app:
    environment:
      - ADD_DEFAULT_ML_BACKENDS=true
      - DEFAULT_ML_BACKEND_URL=http://sam-ml-backend:9090
      - DEFAULT_ML_BACKEND_TITLE=Production SAM Model
      - BASE_DATA_DIR=/label-studio/data
      - LOG_LEVEL=INFO
      - SENTRY_DSN=${SENTRY_DSN}
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          memory: 2G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Related Documentation

- Main ML Backend Config: `knowledge_map/ML_BACKEND_CONFIGURATION.md`
- Environment Variables: `knowledge_map/ENV_TEMPLATE_REFERENCE.md`
- Task Summary: `knowledge_map/task/ml-backend-env-configuration.md`

## Summary

For Docker deployments:
1. ✅ Add environment variables to `docker-compose.yml` (not `.env` in data/)
2. ✅ Use Docker service names for URLs (`sam-ml-backend`, not `localhost`)
3. ✅ Set `BASE_DATA_DIR=/label-studio/data` (container path)
4. ✅ Ensure both services are on the same network
5. ✅ Restart containers after configuration changes

The configuration is now properly set up in your `docker-compose.yml` file.

