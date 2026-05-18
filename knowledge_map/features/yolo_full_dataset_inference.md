# YOLO+SAM2 Full Dataset Pipeline

Biowork exposes a project-level action under:

`Project Settings -> YOLO Inference -> Full Dataset Inference`

This action triggers the external `rustfs_yolo_sam2_inference` Kedro data
processing pipeline. It is not the Label Studio built-in prediction retrieval
path, and it does not call `/api/ml/<backend_id>/predict/project`.

## Flow

1. Biowork lists S3-compatible cloud import storages configured on the current
   project.
2. Biowork lists MLflow runs from the configured shared experiment and the
   project-specific YOLO training experiment. Runs must be tagged or
   parametrized with the current project ID.
3. The user selects the project S3/RustFS dataset and the project MLflow run for
   the newly trained custom YOLO model.
4. The UI calls `POST /api/projects/<project_id>/yolo-sam2-inference/`.
5. Biowork derives the dataset prefix/storage payload and MLflow model URI
   server-side, for example `runs:/<run_id>/weights`.
6. Biowork posts that payload to `BIOWORK_INFERENCE_PIPELINE_URL`, optionally
   with `BIOWORK_INFERENCE_PIPELINE_TOKEN` as a bearer token.
7. The pipeline repo owns the YOLO+SAM2 processing, RustFS reads/writes, MLflow
   model loading, and any generated outputs.

## Configuration

- `BIOWORK_INFERENCE_PIPELINE_URL` must point to the pipeline trigger endpoint.
- `BIOWORK_INFERENCE_PIPELINE_TOKEN` is optional and is sent as bearer auth.
- `BIOWORK_INFERENCE_REQUEST_TIMEOUT` defaults to 30 seconds.
- `BIOWORK_MLFLOW_TRACKING_URI` points Biowork at the product MLflow service.
- `BIOWORK_MLFLOW_EXPERIMENT_NAME` defaults to `biowork-yolo-training`.
- `BIOWORK_MLFLOW_PROJECT_EXPERIMENT_NAME_TEMPLATE` defaults to
  `/data/server/yolo_autotrain/project_{project_id}/runs`.
- `BIOWORK_MLFLOW_MODEL_ARTIFACT_PATH` defaults to `weights`, producing model
  URIs like `runs:/<run_id>/weights` for YOLO runs that store
  `weights/best.pt`.

## Boundaries

Biowork owns the project UI, trigger API, S3-compatible project storage
selection, and project-scoped MLflow run selection. Users do not enter arbitrary
dataset prefixes or MLflow URIs for this workflow. `rustfs_yolo_sam2_inference`
owns the Kedro batch inference implementation that combines YOLO and SAM2 over
the dataset. Label Studio ML backend prediction retrieval remains separate.
