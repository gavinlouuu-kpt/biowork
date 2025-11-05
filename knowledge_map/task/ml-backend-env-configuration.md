# Task: ML Backend Environment Configuration

## Status: COMPLETED

## Objective
Configure Label Studio to use environment variables (.env) to manage the default ML backend URL and ensure all paths reference BASE_DATA_DIR.

## Changes Made

### 1. Updated `.env` File
**Location**: `/Users/reading/Developer/label-studio-custom/data/.env`

**Added Configuration**:
```env
# Base Data Directory Configuration
BASE_DATA_DIR=/Users/reading/Developer/label-studio-custom/data

# ML Backend Configuration
ADD_DEFAULT_ML_BACKENDS=true
DEFAULT_ML_BACKEND_URL=http://localhost:9090
DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
```

**Backup Created**: `data/.env.backup`

### 2. Verified Existing Implementation

The Label Studio codebase already has full support for environment-based ML backend configuration:

#### Settings Loading (`label_studio/core/settings/base.py`)
- Line 25: Loads `.env` file from `data/.env` directory
- Line 140: Reads `BASE_DATA_DIR` from environment variables
- Falls back to `get_data_dir()` if BASE_DATA_DIR is not set

#### ML Backend Settings (`label_studio/core/settings/label_studio.py`)
- Line 19: `ADD_DEFAULT_ML_BACKENDS` - Boolean flag to enable auto-connection
- Line 20: `DEFAULT_ML_BACKEND_URL` - URL of the ML backend server
- Line 21: `DEFAULT_ML_BACKEND_TITLE` - Display name for the backend

#### Auto-Connection Implementation
Two locations automatically connect the ML backend when projects are created:

1. **Server Creation** (`label_studio/server.py`, lines 101-117)
2. **API Creation** (`label_studio/projects/api.py`, lines 273-300)

Both check for `ADD_DEFAULT_ML_BACKENDS` and `DEFAULT_ML_BACKEND_URL` settings.

## How It Works

1. When Label Studio starts, Django loads environment variables from `data/.env`
2. Settings read these variables using `get_env()` function
3. When a new project is created (via UI or API):
   - If `ADD_DEFAULT_ML_BACKENDS=true`
   - And `DEFAULT_ML_BACKEND_URL` is set
   - An MLBackend is automatically created and connected to the project
   - Interactive preannotations are enabled (`is_interactive=True`)
   - UI setting `reveal_preannotations_interactively` is enabled

## Environment Variable Resolution

The `get_env()` function checks variables with these prefixes in order:
1. `LABEL_STUDIO_<NAME>`
2. `HEARTEX_<NAME>`
3. `<NAME>`

Example: For `BASE_DATA_DIR`, it checks:
- `LABEL_STUDIO_BASE_DATA_DIR`
- `HEARTEX_BASE_DATA_DIR`
- `BASE_DATA_DIR`

## Files Modified

1. `/Users/reading/Developer/label-studio-custom/data/.env` - Added configuration
2. `/Users/reading/Developer/label-studio-custom/data/.env.backup` - Created backup

## Documentation Created

1. `/Users/reading/Developer/label-studio-custom/knowledge_map/ML_BACKEND_CONFIGURATION.md`
   - Comprehensive guide explaining the ML backend configuration
   - Details about each environment variable
   - Code references and implementation details
   - Troubleshooting guide

2. `/Users/reading/Developer/label-studio-custom/knowledge_map/task/ml-backend-env-configuration.md` (this file)
   - Task tracking and summary

## Testing Notes

To test the configuration:

1. **Start Label Studio**:
   ```bash
   cd /Users/reading/Developer/label-studio-custom
   python label_studio/manage.py runserver
   ```

2. **Start ML Backend** (in separate terminal):
   ```bash
   cd /Users/reading/Developer/ls-ml-backend-SAM
   # Start your SAM ML backend on port 9090
   ```

3. **Create a New Project**:
   - Log in to Label Studio
   - Create a new project
   - Check that the ML backend is automatically connected
   - Verify the backend appears in Project Settings > Machine Learning

4. **Verify Logs**:
   - Look for "Auto-connected ML backend" messages in logs
   - Check "Database and media directory" shows correct BASE_DATA_DIR

## Configuration Options

### To Change ML Backend URL
Edit `data/.env`:
```env
DEFAULT_ML_BACKEND_URL=http://your-ml-server:port
```

### To Disable Auto-Connection
Edit `data/.env`:
```env
ADD_DEFAULT_ML_BACKENDS=false
```

### To Change Data Directory
Edit `data/.env`:
```env
BASE_DATA_DIR=/path/to/your/data/directory
```

**Note**: After changing `.env`, restart Label Studio for changes to take effect.

## Related Issues/Tasks

- Configuration now centralized in `.env` file
- BASE_DATA_DIR properly references the data directory
- ML backend URL is configurable without code changes
- All paths (database, media, exports) use BASE_DATA_DIR

## Success Criteria

- [x] `.env` file contains BASE_DATA_DIR configuration
- [x] `.env` file contains ML backend configuration
- [x] Existing code already supports environment-based configuration
- [x] Documentation created explaining the configuration
- [x] Backup of original `.env` created
- [x] All paths reference BASE_DATA_DIR from environment

## Next Steps

1. Restart Label Studio to load the new configuration
2. Test creating a new project to verify auto-connection
3. Verify the ML backend appears in the project settings
4. Test interactive preannotations functionality

## Notes

- The Label Studio codebase already had excellent support for environment-based configuration
- No code changes were needed - only configuration updates
- The `.env` file is loaded automatically from the `data/` directory
- Configuration is well-documented in the codebase

