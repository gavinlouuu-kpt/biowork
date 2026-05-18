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
import { Form, Input, Label, Toggle } from "../../components/Form";
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
  const [datasetPrefix, setDatasetPrefix] = useState("");
  const [modelUri, setModelUri] = useState("");

  useEffect(() => {
    if (project?.id) {
      setDatasetPrefix(`biowork/projects/${project.id}`);
    }
  }, [project?.id]);

  const updateProject = useCallback(() => {
    fetchProject(project.id, true);
  }, [fetchProject, project.id]);

  const helperText = useMemo(() => {
    if (!project?.model_version) {
      return "No active inference model is selected.";
    }
    return `Current active inference model/predictions: ${project.model_version}`;
  }, [project?.model_version]);

  const onRunFullDatasetInference = useCallback(async () => {
    if (!modelUri.trim() || runningInference) return;

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
          dataset_prefix: datasetPrefix.trim(),
          ml_backend_id: backend?.id,
          model_uri: modelUri.trim()
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
    datasetPrefix,
    modelUri,
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
                Trigger the project YOLO+SAM2 data processing pipeline with a
                selected MLflow model. This is separate from Label Studio
                prediction retrieval.
              </Description>
              <Input
                skip
                name="inference_dataset_prefix"
                label="Dataset Prefix"
                description="RustFS dataset path used by the pipeline."
                value={datasetPrefix}
                onChange={event => setDatasetPrefix(event.target.value)}
              />
              <Input
                skip
                name="inference_model_uri"
                label="MLflow Model URI"
                description="Example: runs:/<run_id>/model"
                placeholder="runs:/<run_id>/model"
                value={modelUri}
                onChange={event => setModelUri(event.target.value)}
              />
              <div>
                <Button
                  type="button"
                  look="primary"
                  waiting={runningInference}
                  disabled={!modelUri.trim() || runningInference}
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
