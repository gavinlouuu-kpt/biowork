# YOLO Full Dataset Inference

Biowork exposes a project-level full-dataset inference action under:

`Project Settings -> YOLO Inference -> Full Dataset Inference`

The action uses the current project `model_version` selection. It must point to
a live ML backend title, typically the YOLO backend that just finished active
training. Static prediction versions cannot be used as the inference source.

## Flow

1. The UI lists project ML backends and finds the backend whose `title` matches
   the selected `project.model_version`.
2. The UI calls `POST /api/ml/<backend_id>/predict/project`.
3. The backend creates an `MLBackendPredictionJob` row.
4. The job runs `MLBackend.predict_project_tasks()` over every task in the
   project, in batches.
5. Existing predictions for the current backend model version are skipped by
   default. The API supports `overwrite=true` for callers that need to replace
   predictions for the active model version.
6. Returned predictions are saved as normal Label Studio `Prediction` records,
   so they appear in Data Manager and labeling.

## Boundaries

This is the in-product Label Studio prediction path. It applies the selected
live YOLO backend to every task already in the project.

The separate `rustfs_yolo_sam2_inference` repo remains the RustFS/HDF5 Kedro
batch pipeline for running a selected MLflow model over a whole Biowork dataset
outside the Label Studio task table.
