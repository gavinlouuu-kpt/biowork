import { inject } from "mobx-react";
import { observer } from "mobx-react-lite";
import { useCallback, useEffect, useState } from "react";
import { Block, Elem } from "../../utils/bem";
import { Space } from "../Common/Space/Space";
import { Spinner } from "../Common/Spinner";
import "./SegmentationMetricsPane.scss";
import { SegmentationMetricsTable } from "./SegmentationMetricsTable";

const injector = inject(({ store }) => ({
  store,
}));

export const SegmentationMetricsPane = injector(
  observer(({ store }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [rows, setRows] = useState([]);

    const projectId = store.SDK?.projectId;
    const selectedTask = store.taskStore?.selected;
    const taskId = selectedTask?.id;

    const loadMetrics = useCallback(async () => {
      if (!projectId || !taskId) return;

      setLoading(true);
      setError(null);

      try {
        const response = await store.apiCall("segmentationMetrics", {
          projectId,
          task_id: taskId,
        });

        if (!response || response.error) {
          const message = response?.response?.detail ?? response?.error ?? "Unable to load segmentation metrics.";
          setError(message);
          setRows([]);
          return;
        }

        const results = response.results ?? [];
        setRows(results);
      } catch (e) {
        setError("Unable to load segmentation metrics.");
        setRows([]);
      } finally {
        setLoading(false);
      }
    }, [projectId, taskId, store]);

    useEffect(() => {
      loadMetrics();
    }, [loadMetrics]);

    if (!taskId) {
      return (
        <Block name="label-segmetrics">
          <Elem name="empty">Select a task to see segmentation metrics.</Elem>
        </Block>
      );
    }

    return (
      <Block name="label-segmetrics">
        {loading && (
          <Elem name="loading">
            <Space align="center" justify="center">
              <Spinner size={32} />
            </Space>
          </Elem>
        )}
        {!loading && error && (
          <Elem name="error">
            <Space>{error}</Space>
          </Elem>
        )}
        {!loading && !error && rows.length === 0 && (
          <Elem name="empty">
            <Space>No segmentation metrics available for this task.</Space>
          </Elem>
        )}
        {!loading && !error && rows.length > 0 && (
          <Elem name="table">
            <SegmentationMetricsTable rows={rows} />
          </Elem>
        )}
      </Block>
    );
  }),
);


