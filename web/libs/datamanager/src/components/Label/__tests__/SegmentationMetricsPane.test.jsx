import React from "react";
import { render, screen } from "@testing-library/react";
import { Provider } from "mobx-react";
import { SegmentationMetricsPane } from "../SegmentationMetricsPane";

const createStore = (overrides = {}) => {
  return {
    SDK: {
      projectId: 1,
    },
    taskStore: {
      selected: {
        id: 10,
      },
    },
    apiCall: jest.fn().mockResolvedValue({
      count: 1,
      results: [
        {
          image_filename: "image.png",
          task_id: 10,
          annotation_id: 1,
          region_id: 1,
          label: "Object",
          shape_type: "mask",
          bbox_x_px: 0,
          bbox_y_px: 0,
          x_length_px: 10,
          y_length_px: 20,
          area_px: 200,
          mean_gray: 0,
          mean_r: 10,
          mean_g: 20,
          mean_b: 30,
          polygon_points_px: "[]",
        },
      ],
    }),
    ...overrides,
  };
};

describe("SegmentationMetricsPane", () => {
  it("renders empty state when no task is selected", () => {
    const store = createStore({
      taskStore: {
        selected: null,
      },
    });

    render(
      <Provider store={store}>
        <SegmentationMetricsPane />
      </Provider>,
    );

    expect(screen.getByText(/Select a task to see segmentation metrics/i)).toBeInTheDocument();
  });

  it("renders table when metrics are returned", async () => {
    const store = createStore();

    render(
      <Provider store={store}>
        <SegmentationMetricsPane />
      </Provider>,
    );

    expect(await screen.findByText("Image")).toBeInTheDocument();
    expect(await screen.findByText("image.png")).toBeInTheDocument();
  });
});

