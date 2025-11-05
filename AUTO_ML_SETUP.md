# Automatic ML Backend Setup

This Label Studio instance is configured to automatically set up ML backends for new projects.

## Features

When you create a new project, the following happens automatically:

1. **ML Backend Connection**: SAM Model is connected to the project
2. **Model Version Set**: The ML backend is set as the active model
3. **Interactive Preannotations Enabled**: Predictions appear interactively as you annotate

## Configuration

Environment variables (already set in `~/.zshrc`):

```bash
export ADD_DEFAULT_ML_BACKENDS=true
export DEFAULT_ML_BACKEND_URL=http://localhost:9090
export DEFAULT_ML_BACKEND_TITLE="SAM Model"
```

## How to Use

### 1. Start ML Backend

```bash
cd /Users/reading/Developer/label-studio-ml-backend/label_studio_ml/examples/segment_anything_model
./start_local.sh
```

### 2. Start Label Studio

```bash
cd /Users/reading/Developer/label-studio-custom
./start_with_auto_ml.sh
```

### 3. Create a Project

Just create a project normally through the UI - everything is configured automatically!

### 4. Annotate with ML Assistance

1. Import images to your project
2. Open a task for labeling
3. Click on the image
4. SAM will immediately generate segmentation predictions
5. Accept, modify, or reject the predictions

## What Gets Configured Automatically

### Project Settings

When a project is created:

- **Settings > Machine Learning**
  - ML Backend: "SAM Model" (Connected)
  - URL: http://localhost:9090
  - Status: Connected (green)

- **Settings > Labeling Interface**
  - "Show predictions to annotators": ON
  - "Reveal pre-annotations interactively": ON
  - Model Version: "SAM Model"

### Benefits

- **No Manual Configuration**: Everything works out of the box
- **Interactive Experience**: Predictions appear as you annotate
- **Consistent Setup**: All projects have the same ML configuration
- **Time Saving**: No need to configure ML backend for each project

## Verification

After creating a project, verify the setup:

1. Go to **Settings > Machine Learning**
   - Should see "SAM Model" with green "Connected" status

2. Go to **Settings > Labeling Interface**
   - "Reveal pre-annotations interactively" should be checked

3. Try annotating an image:
   - Click on the image
   - SAM should generate segmentation immediately

## Troubleshooting

### ML Backend Not Auto-Connected

Check if ML backend is running:
```bash
curl http://localhost:9090/health
```

Check Label Studio logs for:
```
Auto-connected ML backend "SAM Model" to project X
Enabled interactive preannotations for project X
```

### Interactive Preannotations Not Working

1. Verify setting is enabled:
   - Settings > Labeling Interface
   - "Reveal pre-annotations interactively" should be checked

2. Check ML backend is connected:
   - Settings > Machine Learning
   - Status should be "Connected" (green)

3. Verify label config supports interactive predictions:
   - Must have appropriate tags (e.g., RectangleLabels, PolygonLabels)

## Manual Override

If you want to create a project WITHOUT auto ML backend:

Currently, there's no UI option to disable it per-project. All new projects will have the ML backend auto-connected.

To disable globally:
```bash
# In ~/.zshrc, change:
export ADD_DEFAULT_ML_BACKENDS=false

# Then restart Label Studio
```

## Technical Details

### Modified Files

- `label_studio/core/settings/label_studio.py` - Environment variable configuration
- `label_studio/projects/api.py` - Auto-connection logic for UI/API
- `label_studio/server.py` - Auto-connection logic for CLI

### Code Flow

```
User creates project
    ↓
ProjectListAPI.perform_create() called
    ↓
Project saved to database
    ↓
Check: ADD_DEFAULT_ML_BACKENDS=true?
    ↓ YES
Create MLBackend object
    ↓
Update backend state (health check)
    ↓
Set model_version = "SAM Model"
    ↓
Enable reveal_preannotations_interactively
    ↓
Save project
    ↓
Log success
```

### Database Changes

For each new project:
- 1 row in `ml_backend` table
- Project fields updated:
  - `model_version` = "SAM Model"
  - `reveal_preannotations_interactively` = True

## Related Documentation

- ML Backend: `/Users/reading/Developer/label-studio-ml-backend/label_studio_ml/examples/segment_anything_model/README.md`
- Authentication: `knowledge_map/task/ml_backend_auth_fix_applied.md`
- Multi-org Support: `knowledge_map/features/multi_org_ml_backend.md`

## Support

If you encounter issues:

1. Check ML backend is running and healthy
2. Verify environment variables are set
3. Check Label Studio logs for errors
4. Restart both ML backend and Label Studio

## Summary

This setup provides a seamless experience where:
- New projects automatically connect to SAM
- Interactive predictions work out of the box
- No manual configuration needed
- Consistent experience across all projects

Just start the ML backend, start Label Studio, create a project, and start annotating with ML assistance!
