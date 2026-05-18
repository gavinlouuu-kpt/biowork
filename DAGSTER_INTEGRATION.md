# Dagster Integration

The Dagster orchestrator (`rustfs_yolo_sam2_inference` repo, `dagster_biowork`
package) drives the active-learning loop by calling standard Biowork REST
endpoints.  No Biowork code changes are required; this document records the
contract.

## Endpoints called by Dagster

### Projects

```
GET  /api/projects/           List all projects (paginated via ?next= links)
GET  /api/projects/{id}/      Get project metadata (title, label_config, num_tasks, …)
```

### Tasks / Annotations

```
GET  /api/projects/{id}/export?exportType=JSON
     Export all tasks with their annotations as a JSON array.
     Each element is a task object:
     {
       "id": 1,
       "data": {"image": "<url>"},
       "annotations": [ { "result": [...], "was_cancelled": false } ]
     }
```

```
POST /api/projects/{id}/import
     Bulk-import new tasks into a project (used by future data-import assets).
     Body: [ { "data": { "image": "s3://..." } }, ... ]
```

## Authentication

All requests carry a standard Label Studio token:

```
Authorization: Token <BIOWORK_API_KEY>
```

## How it fits into the Dagster pipeline

```
biowork_project_sensor
  │  polls GET /api/projects/ every 60 s
  │  registers new project IDs as DynamicPartitions
  │  requests active_learning_job runs
  ▼
active_learning_job  (partitioned by project_id)
  ├─ biowork_project      ← GET /api/projects/{id}/
  ├─ biowork_annotations  ← GET /api/projects/{id}/export
  ├─ yolo_trained_model   → POST ml-backend /train
  └─ inference_run        → RustFS + MLflow (no Biowork call)
```

## Required Biowork environment variables (Dagster side)

| Variable | Value |
|----------|-------|
| `BIOWORK_URL` | Internal URL of the Biowork server, e.g. `http://biowork:8080` |
| `BIOWORK_API_KEY` | A valid API token from Biowork's user settings page |
