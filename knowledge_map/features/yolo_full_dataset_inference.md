# YOLO+SAM2 Full Dataset Pipeline

Biowork exposes a project-level action under:

`Project Settings -> YOLO Inference -> Full Dataset Inference`

This action triggers the external `rustfs_yolo_sam2_inference` Kedro data
processing pipeline. It is not the Label Studio built-in prediction retrieval
path, and it does not call `/api/ml/<backend_id>/predict/project`.

## Flow

1. The user selects or enters an MLflow model URI for the newly trained custom
   YOLO model, for example `runs:/<run_id>/model`.
2. The user confirms the RustFS dataset prefix for the current Biowork project.
3. The UI calls `POST /api/projects/<project_id>/yolo-sam2-inference/`.
4. Biowork builds an explicit pipeline payload with project identity, dataset
   prefix, selected MLflow model URI, label config, requester, and optional live
   ML backend context.
5. Biowork posts that payload to `BIOWORK_INFERENCE_PIPELINE_URL`, optionally
   with `BIOWORK_INFERENCE_PIPELINE_TOKEN` as a bearer token.
6. The pipeline repo owns the YOLO+SAM2 processing, RustFS reads/writes, MLflow
   model loading, and any generated outputs.

## Configuration

- `BIOWORK_INFERENCE_PIPELINE_URL` must point to the pipeline trigger endpoint.
- `BIOWORK_INFERENCE_PIPELINE_TOKEN` is optional and is sent as bearer auth.
- `BIOWORK_INFERENCE_DATASET_PREFIX_TEMPLATE` defaults to
  `biowork/projects/{project_id}`.
- `BIOWORK_INFERENCE_REQUEST_TIMEOUT` defaults to 30 seconds.

## Boundaries

Biowork owns the project UI and trigger API. `rustfs_yolo_sam2_inference` owns
the Kedro batch inference implementation that combines YOLO and SAM2 over the
dataset. Label Studio ML backend prediction retrieval remains separate.
