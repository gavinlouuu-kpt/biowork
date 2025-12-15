import { inject } from "mobx-react";
import { observer } from "mobx-react-lite";
import { useCallback, useEffect, useRef, useState } from "react";
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
    const containerRef = useRef(null);

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

    // #region agent log
    useEffect(() => {
      if (!loading && !error && rows.length > 0 && containerRef.current) {
        setTimeout(() => {
          const container = containerRef.current;
          const overlay = container?.closest('.label-view__segmetrics-overlay');
          const tabsRow = document.querySelector('.lsf-annotations-carousel');
          const scrollContainer = container?.querySelector('.segmetrics-table__scroll');
          const tableHeader = container?.querySelector('.segmetrics-table__table thead');
          
          const measurements = {
            overlay: overlay ? {top: overlay.getBoundingClientRect().top, height: overlay.offsetHeight, paddingTop: getComputedStyle(overlay).paddingTop, zIndex: getComputedStyle(overlay).zIndex} : null,
            tabsRow: tabsRow ? {bottom: tabsRow.getBoundingClientRect().bottom, height: tabsRow.offsetHeight, zIndex: getComputedStyle(tabsRow).zIndex} : null,
            container: {top: container.getBoundingClientRect().top, paddingTop: getComputedStyle(container).paddingTop},
            scrollContainer: scrollContainer ? {top: scrollContainer.getBoundingClientRect().top, scrollTop: scrollContainer.scrollTop, borderTop: getComputedStyle(scrollContainer).borderTop} : null,
            tableHeader: tableHeader ? {top: tableHeader.getBoundingClientRect().top, position: getComputedStyle(tableHeader).position, stickyTop: getComputedStyle(tableHeader).top, zIndex: getComputedStyle(tableHeader).zIndex} : null,
            gap: tabsRow && scrollContainer ? scrollContainer.getBoundingClientRect().top - tabsRow.getBoundingClientRect().bottom : null
          };
          
          fetch('http://localhost:7242/ingest/72ea390b-662d-4988-92ef-c2108a4eb656',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'SegmentationMetricsPane.jsx:70',message:'Layout measurements on mount',data:measurements,timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H1,H2,H4,H5'})}).catch(()=>{});
        }, 100);
      }
    }, [loading, error, rows.length]);
    // #endregion

    if (!taskId) {
      return (
        <Block name="label-segmetrics">
          <Elem name="empty">Select a task to see segmentation metrics.</Elem>
        </Block>
      );
    }

    return (
      <Block name="label-segmetrics" ref={containerRef}>
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


