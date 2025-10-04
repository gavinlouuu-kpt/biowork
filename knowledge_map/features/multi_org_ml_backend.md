# Multi-Organization ML Backend Support

## Overview

This document describes the middleware solution that enables the ML backend (specifically SAM - Segment Anything Model) to automatically retrieve and use appropriate organization API tokens without requiring manual configuration from users.

## Problem Statement

Previously, Label Studio's ML backend required each organization to manually configure their API token in the ML backend settings. This created several issues:

1. **Manual Configuration**: Each organization needed to manually set up their API token
2. **Security Concerns**: API tokens had to be shared and configured externally
3. **Maintenance Overhead**: Token updates required manual reconfiguration
4. **Multi-Org Isolation**: Modified Label Studio setup ensures each user gets their own organization upon signup, but ML backend couldn't automatically adapt to this

## Solution Architecture

### Components

1. **Organization API Middleware** (`org_api_middleware.py`)
   - Connects to Label Studio's SQLite database
   - Retrieves organization information based on project IDs
   - Fetches API tokens for organization admins
   - Provides caching for performance optimization

2. **Enhanced SAM Predictor** (`sam_predictor.py`)
   - Dynamically resolves credentials using the middleware
   - Falls back to static tokens if middleware is disabled
   - Maintains backward compatibility

3. **Docker Configuration** (`docker-compose.yml`)
   - Mounts Label Studio database as read-only volume
   - Configures environment variables for middleware operation

## Database Schema

The middleware queries the following Label Studio database tables:

```sql
-- Project to Organization mapping
SELECT organization_id FROM project WHERE id = ?

-- Organization creator (admin)
SELECT created_by_id FROM organization WHERE id = ?

-- User's authentication token
SELECT key FROM authtoken_token WHERE user_id = ?
```

## Configuration

### Environment Variables

#### Multi-Organization Mode (Recommended)

```bash
# Enable organization middleware
USE_ORG_MIDDLEWARE=true

# Path to Label Studio database
LABEL_STUDIO_DB_PATH=/label-studio-data/label_studio.sqlite3

# Label Studio host URL
LABEL_STUDIO_HOST=http://host.docker.internal:8080
```

#### Legacy Mode (Fallback)

```bash
# Disable middleware
USE_ORG_MIDDLEWARE=false

# Static credentials
LABEL_STUDIO_ACCESS_TOKEN=your-static-token-here
LABEL_STUDIO_HOST=http://host.docker.internal:8080
```

### Docker Compose Setup

Update your `docker-compose.yml`:

```yaml
volumes:
  - "./data/server:/data"
  # Mount Label Studio database for multi-organization support
  - "/Users/reading/Developer/label-studio-custom/data:/label-studio-data:ro"
```

**Important**: The database must be mounted as read-only (`:ro`) to prevent accidental modifications.

## How It Works

### Request Flow

1. **User Initiates Prediction**
   - User in Organization A makes an annotation request
   - Request includes task with project ID reference

2. **Middleware Intercepts**
   - SAM predictor receives task with project information
   - Middleware extracts project ID from task data
   - Format: `"project": "123.1609459200"` (project_id.timestamp)

3. **Database Lookup**
   - Query 1: Find organization_id for the project
   - Query 2: Find organization creator (admin user)
   - Query 3: Retrieve admin user's auth token

4. **Dynamic Credential Usage**
   - Use retrieved credentials for this specific request
   - Download image using organization-specific token
   - Run inference and return results

5. **Caching**
   - Project → Organization mappings are cached
   - Organization → Token mappings are cached
   - Cache invalidation available via API

### Code Flow

```python
# In sam_predictor.py
def set_image(self, img_path, calculate_embeddings=True, task=None):
    # Default to static credentials
    access_token = LABEL_STUDIO_ACCESS_TOKEN
    hostname = LABEL_STUDIO_HOST
    
    # Try dynamic credentials if middleware enabled
    if USE_ORG_MIDDLEWARE and task:
        middleware = get_middleware()
        project_id = task['project']
        hostname, access_token = middleware.get_credentials_for_project(project_id)
    
    # Use credentials to fetch image
    image_path = get_local_path(img_path, access_token=access_token, hostname=hostname)
```

## Security Considerations

### Database Access

- Database is mounted **read-only** to prevent modifications
- Only SELECT queries are performed
- No write operations to the database

### Token Security

- Tokens are retrieved dynamically per-request
- Tokens are cached in memory only (not persisted)
- Cache can be cleared on demand
- No tokens are logged (only debug info about success/failure)

### Isolation

- Each organization's tokens are isolated
- Cross-organization access is prevented by Label Studio's own access controls
- ML backend respects organization boundaries

## Performance

### Caching Strategy

- **LRU Cache**: Stores up to 128 project→org and org→token mappings
- **Cache Hit**: Sub-millisecond lookup
- **Cache Miss**: ~10-50ms database query
- **Cache Persistence**: In-memory only, cleared on restart

### Optimization Tips

1. **Pre-warm Cache**: First request per project is slower
2. **Database Location**: Use local filesystem for database (not network mount)
3. **Connection Pooling**: SQLite connections are created per-query (lightweight)

## Troubleshooting

### Common Issues

#### 1. Database Not Found

**Error**: `Database file not found at /label-studio-data/label_studio.sqlite3`

**Solution**: 
- Verify Label Studio data path is correctly mounted
- Check Docker volume configuration
- Ensure Label Studio is using SQLite (not PostgreSQL)

#### 2. No Token Found

**Error**: `No auth token found for user X in organization Y`

**Solution**:
- Verify organization admin has generated an API token
- Check token exists in Label Studio UI → Account & Settings → Access Token
- Ensure user is organization creator or admin

#### 3. Permission Denied

**Error**: `Permission denied: /label-studio-data/label_studio.sqlite3`

**Solution**:
- Check file permissions on mounted volume
- Ensure ML backend container has read permissions
- Verify SELinux/AppArmor policies if applicable

#### 4. Wrong Organization Credentials

**Error**: ML backend uses wrong organization's token

**Solution**:
- Clear middleware cache: restart ML backend
- Verify project→organization mapping in database
- Check logs for project ID parsing

### Debug Mode

Enable debug logging:

```yaml
environment:
  - LOG_LEVEL=DEBUG
```

Debug logs show:
- Middleware initialization
- Database queries
- Credential resolution
- Cache hits/misses

## Migration Guide

### From Static Tokens to Middleware

1. **Backup Configuration**
   ```bash
   # Save current docker-compose.yml
   cp docker-compose.yml docker-compose.yml.backup
   ```

2. **Update docker-compose.yml**
   - Add database volume mount
   - Set `USE_ORG_MIDDLEWARE=true`
   - Set `LABEL_STUDIO_DB_PATH`

3. **Test with One Organization**
   - Keep `LABEL_STUDIO_ACCESS_TOKEN` as fallback
   - Monitor logs for successful middleware usage
   - Verify predictions work correctly

4. **Full Deployment**
   - Remove static token after successful test
   - Deploy to all ML backend instances

### Rollback Plan

If issues occur:

1. Set `USE_ORG_MIDDLEWARE=false`
2. Restore `LABEL_STUDIO_ACCESS_TOKEN`
3. Restart ML backend
4. Static token mode will be used

## Testing

### Manual Testing

1. **Create Test Organizations**
   ```bash
   # In Label Studio
   # Create Org A with User A
   # Create Org B with User B
   ```

2. **Create Test Projects**
   ```bash
   # Create Project 1 in Org A
   # Create Project 2 in Org B
   ```

3. **Test Predictions**
   ```bash
   # User A: Make prediction in Project 1
   # Expected: Uses Org A's token
   
   # User B: Make prediction in Project 2
   # Expected: Uses Org B's token
   ```

4. **Verify Logs**
   ```bash
   docker logs segment_anything_model | grep "Using dynamic credentials"
   ```

### Automated Testing

Create test script:

```python
from org_api_middleware import OrganizationAPIMiddleware

# Initialize middleware
middleware = OrganizationAPIMiddleware(
    db_path='/path/to/test_db.sqlite3',
    label_studio_host='http://localhost:8080'
)

# Test project lookup
org_id = middleware.get_project_organization(1)
assert org_id is not None

# Test token retrieval
hostname, token = middleware.get_credentials_for_project(1)
assert hostname and token
```

## Future Enhancements

### Planned Features

1. **PostgreSQL Support**
   - Add database abstraction layer
   - Support multiple database backends

2. **Token Rotation**
   - Detect expired tokens
   - Automatic refresh mechanism

3. **User-Specific Tokens**
   - Use annotator's token instead of admin
   - Better audit trail

4. **Health Checks**
   - Periodic database connectivity check
   - Token validity verification
   - Automatic failover to static credentials

5. **Metrics**
   - Track cache hit/miss rates
   - Monitor credential resolution time
   - Alert on failures

## References

- Label Studio Database Schema: `label-studio-custom/label_studio/organizations/models.py`
- ML Backend API: `label-studio-ml-backend/label_studio_ml/api.py`
- SAM Backend: `label-studio-ml-backend/label_studio_ml/examples/segment_anything_model/`

## Support

For issues or questions:
1. Check troubleshooting section above
2. Enable debug logging
3. Review ML backend logs
4. Check Label Studio database consistency
5. Verify organization and project setup

## Change Log

### Version 1.0 (2025-10-04)
- Initial implementation
- SQLite support
- LRU caching
- Backward compatibility with static tokens
- Docker Compose configuration

