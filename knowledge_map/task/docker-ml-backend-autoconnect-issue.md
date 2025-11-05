# Docker ML Backend Auto-Connect Issue

## Issue Summary

Label Studio deployed via Docker Compose was not automatically establishing ML backend connections when creating new projects, despite having the proper environment variables configured in `docker-compose.yml`.

## Root Cause

The Label Studio containers were created **before** the ML backend environment variables were added to `docker-compose.yml`. Docker Compose only injects environment variables into containers at **creation time**, not when the configuration file is modified.

### Timeline
- Container created: 2025-10-05T23:12:34Z
- docker-compose.yml modified: Oct 6 10:25:20 2025 (after container creation)
- Result: Environment variables missing from running container

### Verification
```bash
# Check environment variables in running container
docker exec label-studio-app printenv | grep -E "(ADD_DEFAULT|DEFAULT_ML)"
# Result: No output (variables missing)
```

## Environment Variables Required

These variables must be present in the Label Studio container for auto-connection to work:

```yaml
environment:
  - ADD_DEFAULT_ML_BACKENDS=true
  - DEFAULT_ML_BACKEND_URL=http://sam-ml-backend:9090
  - DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
```

### How Label Studio Uses These Variables

From `/label_studio/core/settings/label_studio.py`:
```python
ADD_DEFAULT_ML_BACKENDS = get_bool_env('ADD_DEFAULT_ML_BACKENDS', False)
DEFAULT_ML_BACKEND_URL = get_env('DEFAULT_ML_BACKEND_URL', '')
DEFAULT_ML_BACKEND_TITLE = get_env('DEFAULT_ML_BACKEND_TITLE', 'Default ML Backend')
```

Auto-connection logic in `/label_studio/projects/api.py`:
```python
if settings.ADD_DEFAULT_ML_BACKENDS and settings.DEFAULT_ML_BACKEND_URL:
    ml_backend = MLBackend.objects.create(
        project=project,
        url=settings.DEFAULT_ML_BACKEND_URL,
        title=settings.DEFAULT_ML_BACKEND_TITLE,
        is_interactive=True
    )
```

## Solution

Recreate the containers to pick up the environment variables:

```bash
cd /Users/reading/Developer/label-studio-custom
docker-compose down
docker-compose up -d
```

### Verification After Fix
```bash
docker exec label-studio-app printenv | grep -E "(ADD_DEFAULT|DEFAULT_ML)"
```

Expected output:
```
ADD_DEFAULT_ML_BACKENDS=true
DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
DEFAULT_ML_BACKEND_URL=http://sam-ml-backend:9090
```

## Network Configuration

Both containers must be on the same Docker network for communication:

```bash
# Verify network connectivity
docker network inspect label-studio-network --format='{{range .Containers}}{{.Name}} {{end}}'
```

Expected output should include:
- label-studio-app
- label-studio-db
- sam-ml-backend
- label-studio-nginx

## Testing Auto-Connection

After restarting containers:

1. Access Label Studio at http://localhost:8080
2. Create a new project
3. Go to Settings > Machine Learning
4. Verify "SAM Interactive Segmentation" backend is automatically connected
5. Status should show as "Connected" (green indicator)

## Important Notes

1. **Container Recreation Required**: Changing environment variables in `docker-compose.yml` requires recreating containers with `docker-compose down && docker-compose up -d`

2. **Not a Restart**: Simply restarting containers (`docker-compose restart`) will NOT pick up new environment variables

3. **Existing Projects**: This auto-connection only applies to **newly created projects**. Existing projects require manual ML backend connection

4. **Network Names**: Use Docker service names (e.g., `sam-ml-backend`) not `localhost` in `DEFAULT_ML_BACKEND_URL` when containers are in the same Docker network

## Related Files

- `/Users/reading/Developer/label-studio-custom/docker-compose.yml` - Container configuration
- `/label_studio/core/settings/label_studio.py` - Environment variable definitions
- `/label_studio/projects/api.py` - Auto-connection implementation
- `/label_studio/server.py` - Alternative auto-connection path

## Status

**RESOLVED** - Containers recreated with proper environment variables. Auto-connection now working for new projects.

Date: 2025-10-05

