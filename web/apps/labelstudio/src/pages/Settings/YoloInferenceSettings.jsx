import { ToastType, useToast } from "@humansignal/ui";
import {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState
} from "react";
import { Button } from "../../components";
import { Description } from "../../components/Description/Description";
import { Form, Label, Select, Toggle } from "../../components/Form";
import { Divider } from "../../components/Divider/Divider";
import { Block, Elem } from "../../utils/bem";
import { ModelVersionSelector } from "./AnnotationSettings/ModelVersionSelector";
import { ProjectContext } from "../../providers/ProjectProvider";
import { useAPI } from "../../providers/ApiProvider";

export const YoloInferenceSettings = () => {
  const api = useAPI();
  const toast = useToast();
  const { project, fetchProject } = useContext(ProjectContext);
  const formRef = useRef();
  const [runningInference, setRunningInference] = useState(false);
  const [lastInferenceResult, setLastInferenceResult] = useState(null);
  const [loadingInferenceContext, setLoadingInferenceContext] = useState(false);
  const [inferenceContext, setInferenceContext] = useState(null);
  const [datasetStorageKey, setDatasetStorageKey] = useState("");
  const [modelRunId, setModelRunId] = useState("");

  const fetchInferenceContext = useCallback(async () => {
    if (!project?.id) return;

    setLoadingInferenceContext(true);
    try {
      const response = await api.callApi("projectYoloSam2InferenceContext", {
        params: { pk: project.id }
      });
      setInferenceContext(response);
      setDatasetStorageKey(response?.dataset_storage?.key ?? "");
      setModelRunId(response?.model_runs?.[0]?.run_id ?? "");
    } finally {
      setLoadingInferenceContext(false);
    }
  }, [api, project?.id]);

  useEffect(() => {
    fetchInferenceContext();
  }, [fetchInferenceContext]);

  const updateProject = useCallback(() => {
    fetchProject(project.id, true);
  }, [fetchProject, project.id]);

  const helperText = useMemo(() => {
    if (!project?.model_version) {
      return "No active inference model is selected.";
    }
    return `Current active inference model/predictions: ${project.model_version}`;
  }, [project?.model_version]);

  const datasetStorageOptions = useMemo(() => {
    return (inferenceContext?.dataset_storages ?? []).map(storage => ({
      label: storage.label,
      value: storage.key
    }));
  }, [inferenceContext?.dataset_storages]);

  const modelRunOptions = useMemo(() => {
    return (inferenceContext?.model_runs ?? []).map(run => ({
      label: run.label ? `${run.label} (${run.run_id})` : run.run_id,
      value: run.run_id
    }));
  }, [inferenceContext?.model_runs]);

  const selectedStorage = useMemo(() => {
    return (inferenceContext?.dataset_storages ?? []).find(
      storage => storage.key === datasetStorageKey
    );
  }, [datasetStorageKey, inferenceContext?.dataset_storages]);

  const selectedRun = useMemo(() => {
    return (inferenceContext?.model_runs ?? []).find(
      run => run.run_id === modelRunId
    );
  }, [inferenceContext?.model_runs, modelRunId]);

  const onRunFullDatasetInference = useCallback(async () => {
    if (!datasetStorageKey || !modelRunId || runningInference) return;

    setRunningInference(true);
    setLastInferenceResult(null);
    try {
      let backend;

      if (project?.model_version) {
        const mlBackends = await api.callApi("mlBackends", {
          params: { project: project.id }
        });
        backend = (mlBackends ?? []).find(
          item => item.title === project.model_version
        );
      }

      const response = await api.callApi("projectYoloSam2Inference", {
        params: { pk: project.id },
        body: {
          dataset_storage_key: datasetStorageKey,
          ml_backend_id: backend?.id,
          model_run_id: modelRunId
        }
      });

      if (!response) return;

      setLastInferenceResult(response);
      const queued = response.status === "queued";
      toast.show({
        message: queued
          ? "YOLO+SAM2 pipeline has been queued."
          : "YOLO+SAM2 pipeline has been triggered.",
        type: ToastType.info
      });
    } catch (error) {
      toast.show({
        message:
          error?.response?.detail ??
          error?.message ??
          "Could not trigger YOLO+SAM2 pipeline.",
        type: ToastType.error
      });
    } finally {
      setRunningInference(false);
    }
  }, [
    api,
    datasetStorageKey,
    modelRunId,
    project?.id,
    project?.model_version,
    runningInference,
    toast
  ]);

  return (
    <Block name="yolo-inference-settings">
      <Elem name={"wrapper"}>
        <h1>YOLO Inference</h1>
        <Block name="settings-wrapper">
          <Form
            ref={formRef}
            action="updateProject"
            formData={{ ...project }}
            params={{ pk: project.id }}
            onSubmit={updateProject}
          >
            <Form.Row columnCount={1}>
              <Label text="Inference Source" large />
              <Description style={{ marginTop: 0, maxWidth: 760 }}>
                Configure which live model or prediction set is used for
                prelabeling and uncertainty-driven task ordering. For YOLO
                workflows, select your trained YOLO backend title here.
              </Description>
              <Description style={{ marginTop: 0 }}>{helperText}</Description>
              <div>
                <Toggle
                  label="Use predictions to prelabel tasks"
                  description="Enable predictions in labeling UI."
                  name="show_collab_predictions"
                />
              </div>
              <ModelVersionSelector />
              <div>
                <Toggle
                  label="Reveal interactive preannotations"
                  description="Keep this enabled if you still want SAM interactive assist while YOLO remains the inference source."
                  name="reveal_preannotations_interactively"
                />
              </div>
            </Form.Row>

            <Divider height={32} />

            <Form.Row columnCount={1}>
              <Label text="Task Sampling" large />
              <Description style={{ marginTop: 0, maxWidth: 760 }}>
                Set project sampling mode to Uncertainty sampling in General
                settings if you want active-learning prioritization driven by
                this selected inference model.
              </Description>
            </Form.Row>

            <Divider height={32} />

            <Form.Row columnCount={1}>
              <Label text="Full Dataset Inference" large />
              <Description style={{ marginTop: 0, maxWidth: 760 }}>
                Trigger the project YOLO+SAM2 data processing pipeline using
                this project's cloud storage and MLflow training runs. This is
                separate from Label Studio prediction retrieval.
              </Description>
              <Select
                skip
                name="inference_dataset_storage"
                label="Cloud Storage Dataset"
                disabled={
                  !datasetStorageOptions.length || loadingInferenceContext
                }
                isInProgress={loadingInferenceContext}
                options={datasetStorageOptions}
                placeholder="No cloud storage configured"
                value={datasetStorageKey}
                onChange={setDatasetStorageKey}
              />
              {selectedStorage && (
                <Description style={{ marginTop: 0, maxWidth: 760 }}>
                  Dataset source: {selectedStorage.uri}
                </Description>
              )}
              <Select
                skip
                name="inference_model_run"
                label="Project MLflow Run"
                disabled={!modelRunOptions.length || loadingInferenceContext}
                isInProgress={loadingInferenceContext}
                options={modelRunOptions}
                placeholder="No project MLflow runs found"
                value={modelRunId}
                onChange={setModelRunId}
              />
              {selectedRun && (
                <Description style={{ marginTop: 0, maxWidth: 760 }}>
                  Model URI: {selectedRun.model_uri}
                </Description>
              )}
              <div>
                <Button
                  type="button"
                  look="primary"
                  waiting={runningInference}
                  disabled={
                    !datasetStorageKey ||
                    !modelRunId ||
                    runningInference ||
                    loadingInferenceContext
                  }
                  onClick={onRunFullDatasetInference}
                >
                  Run YOLO+SAM2 Pipeline
                </Button>
              </div>
              {lastInferenceResult && (
                <Description style={{ marginTop: 12, maxWidth: 760 }}>
                  {lastInferenceResult.status === "queued"
                    ? `Queued pipeline job ${lastInferenceResult.job_id}.`
                    : `Pipeline responded with HTTP ${lastInferenceResult
                        .pipeline_response?.status_code ?? "OK"}.`}
                </Description>
              )}
            </Form.Row>

            <Form.Actions>
              <Form.Indicator>
                <span case="success">Saved!</span>
              </Form.Indicator>
              <Button type="submit" look="primary" style={{ width: 120 }}>
                Save
              </Button>
            </Form.Actions>
          </Form>
        </Block>
      </Elem>
    </Block>
  );
};

YoloInferenceSettings.title = "YOLO Inference";
YoloInferenceSettings.path = "/yolo-inference";
