import { ToastType, useToast } from "@humansignal/ui";
import { useCallback, useContext, useMemo, useRef, useState } from "react";
import { Button } from "../../components";
import { Description } from "../../components/Description/Description";
import { Form, Label, Toggle } from "../../components/Form";
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
    if (!project?.model_version || runningInference) return;

    setRunningInference(true);
    setLastInferenceResult(null);
    try {
      const mlBackends = await api.callApi("mlBackends", {
        params: { project: project.id }
      });
      const backend = (mlBackends ?? []).find(
        item => item.title === project.model_version
      );

      if (!backend) {
        toast.show({
          message:
            "Select a live YOLO model backend before running full dataset inference.",
          type: ToastType.error
        });
        return;
      }

      const response = await api.callApi("predictProjectWithML", {
        params: { pk: backend.id },
        body: { batch_size: 100 }
      });

      if (!response) return;

      setLastInferenceResult(response);
      const queued = response.status === "queued";
      toast.show({
        message: queued
          ? "Full dataset inference has been queued."
          : "Full dataset inference has completed.",
        type: ToastType.info
      });
      await fetchProject(project.id, true);
    } finally {
      setRunningInference(false);
    }
  }, [
    api,
    fetchProject,
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
                Run the selected live YOLO backend over every task in this
                project and save returned predictions for review in Data Manager
                and labeling. Save this page first if you changed the inference
                source above.
              </Description>
              <div>
                <Button
                  type="button"
                  look="primary"
                  waiting={runningInference}
                  disabled={!project?.model_version || runningInference}
                  onClick={onRunFullDatasetInference}
                >
                  Run Inference on Full Dataset
                </Button>
              </div>
              {lastInferenceResult && (
                <Description style={{ marginTop: 12, maxWidth: 760 }}>
                  {lastInferenceResult.status === "queued"
                    ? `Queued ${lastInferenceResult.total_tasks} tasks for inference.`
                    : `Created ${lastInferenceResult.result
                        ?.created_predictions ??
                        0} predictions from ${lastInferenceResult.result
                        ?.total_tasks ?? 0} tasks.`}
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
