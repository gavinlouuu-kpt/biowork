# ML Backend Configuration Guide

## Overview

Label Studio supports automatic connection of Machine Learning backends to projects. This is configured through environment variables managed in the `.env` file located in the data directory.

## Configuration Location

The configuration is managed through the `.env` file at:
```
/Users/reading/Developer/label-studio-custom/data/.env
```

This file is automatically loaded by Django settings at startup via:
```python
# label_studio/core/settings/base.py, line 25
env.read_env(os.path.join(os.path.dirname(__file__), '../../../data/.env'))
```

## Environment Variables

### BASE_DATA_DIR
- **Purpose**: Sets the base directory for Label Studio data (media files, exports, database)
- **Example**: `BASE_DATA_DIR=/Users/reading/Developer/label-studio-custom/data`
- **Used in**: `label_studio/core/settings/base.py`, line 140
- **Fallback**: If not set, uses `get_data_dir()` which returns the user data directory

### ADD_DEFAULT_ML_BACKENDS
- **Purpose**: Enable/disable automatic connection of default ML backend to new projects
- **Type**: Boolean (`true` or `false`)
- **Example**: `ADD_DEFAULT_ML_BACKENDS=true`
- **Used in**: `label_studio/core/settings/label_studio.py`, line 19

### DEFAULT_ML_BACKEND_URL
- **Purpose**: URL of the default ML backend server that will be automatically connected
- **Example**: `DEFAULT_ML_BACKEND_URL=http://localhost:9090`
- **Used in**: 
  - `label_studio/core/settings/label_studio.py`, line 20
  - `label_studio/server.py`, line 107 (project creation)
  - `label_studio/projects/api.py`, line 278 (API project creation)

### DEFAULT_ML_BACKEND_TITLE
- **Purpose**: Display name for the default ML backend in the UI
- **Example**: `DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation`
- **Used in**: `label_studio/core/settings/label_studio.py`, line 21
- **Default**: "Default ML Backend"

## How It Works

### Automatic ML Backend Connection

When a new project is created, Label Studio automatically connects the default ML backend if:
1. `ADD_DEFAULT_ML_BACKENDS=true` in the `.env` file
2. `DEFAULT_ML_BACKEND_URL` is set to a valid URL

This happens in two places:

#### 1. Server Project Creation (`label_studio/server.py`)
```python
elif settings.ADD_DEFAULT_ML_BACKENDS and settings.DEFAULT_ML_BACKEND_URL:
    ml_backend = MLBackend.objects.create(
        project=project,
        url=settings.DEFAULT_ML_BACKEND_URL,
        title=settings.DEFAULT_ML_BACKEND_TITLE,
        is_interactive=True  # Enable interactive preannotations
    )
```

#### 2. API Project Creation (`label_studio/projects/api.py`)
```python
if settings.ADD_DEFAULT_ML_BACKENDS and settings.DEFAULT_ML_BACKEND_URL:
    ml_backend = MLBackend.objects.create(
        project=project,
        url=settings.DEFAULT_ML_BACKEND_URL,
        title=settings.DEFAULT_ML_BACKEND_TITLE,
        is_interactive=True
    )
    ml_backend.update_state()
```

### Interactive Preannotations

When the default ML backend is connected, the following features are automatically enabled:
- `is_interactive=True`: Enables interactive annotation with the ML model
- `reveal_preannotations_interactively`: Shows predictions as the user interacts with tasks

## Current Configuration

As of the latest setup, the `.env` file contains:

```env
# Base Data Directory Configuration
BASE_DATA_DIR=/Users/reading/Developer/label-studio-custom/data

# ML Backend Configuration
ADD_DEFAULT_ML_BACKENDS=true
DEFAULT_ML_BACKEND_URL=http://localhost:9090
DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
```

## Environment Variable Resolution

The `get_env()` function checks environment variables in the following order:
1. `LABEL_STUDIO_<NAME>`
2. `HEARTEX_<NAME>`
3. `<NAME>`

This allows for flexible configuration through different prefixes.

## Usage Example

### For SAM (Segment Anything Model) Backend

If you're running a SAM ML backend on port 9090:

```env
ADD_DEFAULT_ML_BACKENDS=true
DEFAULT_ML_BACKEND_URL=http://localhost:9090
DEFAULT_ML_BACKEND_TITLE=SAM Interactive Segmentation
```

### For Custom ML Backend

If you have a custom ML backend on a different host:

```env
ADD_DEFAULT_ML_BACKENDS=true
DEFAULT_ML_BACKEND_URL=http://ml-server.example.com:8080
DEFAULT_ML_BACKEND_TITLE=My Custom Model
```

### Disable Auto-Connection

To disable automatic ML backend connection:

```env
ADD_DEFAULT_ML_BACKENDS=false
```

## Related Files

- **Settings Configuration**: 
  - `label_studio/core/settings/base.py` - Base settings and BASE_DATA_DIR
  - `label_studio/core/settings/label_studio.py` - ML backend settings
  
- **ML Backend Models**: 
  - `label_studio/ml/models.py` - MLBackend database model
  - `label_studio/ml/api.py` - ML backend API endpoints
  
- **Project Creation**: 
  - `label_studio/server.py` - Server-side project creation
  - `label_studio/projects/api.py` - API project creation

## Troubleshooting

### ML Backend Not Connecting

1. Check that `ADD_DEFAULT_ML_BACKENDS=true` in `.env`
2. Verify `DEFAULT_ML_BACKEND_URL` is set and accessible
3. Check Label Studio logs for connection errors
4. Ensure the ML backend server is running and responding to health checks

### BASE_DATA_DIR Not Being Used

1. Verify the `.env` file is at `/path/to/label-studio-custom/data/.env`
2. Check file permissions on the `.env` file
3. Restart Label Studio after changing environment variables
4. Check logs for "Database and media directory" message

## Notes

- Environment variables are loaded once at Django startup
- Changes to `.env` require a Label Studio restart to take effect
- The `.env` file should not be committed to version control if it contains sensitive information
- Backup file created at: `data/.env.backup`

