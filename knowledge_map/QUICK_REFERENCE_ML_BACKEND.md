# Quick Reference: ML Backend Configuration

## TL;DR

### Docker Deployment (Current Setup)
```bash
# Configuration is in docker-compose.yml
# No need for .env file in data/ directory

# Restart to apply changes:
cd /Users/reading/Developer/label-studio-custom
docker-compose restart app

# Verify:
docker exec label-studio-app env | grep ML_BACKEND
```

### Local Development (Non-Docker)
```bash
# Configuration is in data/.env file
# Edit: /Users/reading/Developer/label-studio-custom/data/.env

# Restart Label Studio to apply changes
```

## Configuration Quick Copy-Paste

### Docker (docker-compose.yml)
```yaml
environment:
  - ADD_DEFAULT_ML_BACKENDS=true
  - DEFAULT_ML_BACKEND_URL=http://sam-ml-backend:9090
  - DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
  - BASE_DATA_DIR=/label-studio/data
```

### Local Dev (data/.env)
```env
ADD_DEFAULT_ML_BACKENDS=true
DEFAULT_ML_BACKEND_URL=http://localhost:9090
DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
BASE_DATA_DIR=/Users/reading/Developer/label-studio-custom/data
```

## Key Differences

| Setting | Docker | Local Dev |
|---------|--------|-----------|
| ML Backend URL | `http://sam-ml-backend:9090` | `http://localhost:9090` |
| BASE_DATA_DIR | `/label-studio/data` | Full host path |
| Config File | `docker-compose.yml` | `data/.env` |

## Testing Checklist

- [ ] Environment variables set correctly
- [ ] Label Studio restarted
- [ ] SAM ML backend is running
- [ ] Network connectivity works (Docker only)
- [ ] New project created
- [ ] ML backend auto-connected
- [ ] Interactive preannotations work

## Common Commands

### Docker
```bash
# Restart
docker-compose restart app

# Check env vars
docker exec label-studio-app env | grep ML_BACKEND

# Check network
docker exec label-studio-app curl http://sam-ml-backend:9090/health

# View logs
docker logs label-studio-app | grep -i "ml backend"
```

### Local Dev
```bash
# Start Label Studio
python label_studio/manage.py runserver

# Check env vars
env | grep ML_BACKEND
```

## Troubleshooting One-Liners

```bash
# Can't connect to ML backend (Docker)
docker exec label-studio-app ping sam-ml-backend

# Environment variables not loading
docker-compose down && docker-compose up -d

# Check if SAM backend is running
docker ps | grep sam-ml-backend

# View Label Studio startup logs
docker logs label-studio-app --tail 50
```

## Documentation Links

- Full Docker Guide: `knowledge_map/DOCKER_ML_BACKEND_CONFIGURATION.md`
- Local Dev Guide: `knowledge_map/ML_BACKEND_CONFIGURATION.md`
- All Environment Variables: `knowledge_map/ENV_TEMPLATE_REFERENCE.md`
- Task Summary: `knowledge_map/task/docker-ml-backend-configuration.md`

## What Was Changed

1. **docker-compose.yml** - Added ML backend environment variables
2. **data/.env** - Still valid for local development
3. Documentation created for both approaches

## Next Steps

1. Restart Label Studio container: `docker-compose restart app`
2. Create a new project to test auto-connection
3. Verify "SAM Interactive Segmentation" appears in ML settings

