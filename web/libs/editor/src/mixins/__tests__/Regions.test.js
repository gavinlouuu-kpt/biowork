import { isConnectedDynamicRegion } from "../dynamicPromptRegions";

const region = (type, { labelName = "Object", toName = "image", dynamic = false } = {}) => ({
  type,
  labelName,
  dynamic,
  results: [{ to_name: toName }],
});

describe("Regions dynamic prompt grouping", () => {
  it("groups active smart keypoint and rectangle prompts for the same label and image", () => {
    expect(isConnectedDynamicRegion(region("keypointregion", { dynamic: true }), region("rectangleregion", { dynamic: true }))).toBe(true);
    expect(isConnectedDynamicRegion(region("rectangleregion", { dynamic: true }), region("keypointregion", { dynamic: true }))).toBe(true);
  });

  it("does not group inactive prompt-region annotations into active prompt requests", () => {
    expect(isConnectedDynamicRegion(region("keypointregion", { dynamic: true }), region("rectangleregion"))).toBe(false);
    expect(isConnectedDynamicRegion(region("rectangleregion", { dynamic: true }), region("keypointregion"))).toBe(false);
  });

  it("does not group prompt regions across labels or target objects", () => {
    expect(
      isConnectedDynamicRegion(
        region("keypointregion", { dynamic: true }),
        region("rectangleregion", { dynamic: true, labelName: "Other" }),
      ),
    ).toBe(false);
    expect(
      isConnectedDynamicRegion(
        region("keypointregion", { dynamic: true }),
        region("rectangleregion", { dynamic: true, toName: "other-image" }),
      ),
    ).toBe(false);
  });

  it("preserves same-type grouping for non-prompt regions", () => {
    expect(isConnectedDynamicRegion(region("polygonregion"), region("polygonregion"))).toBe(true);
    expect(isConnectedDynamicRegion(region("polygonregion"), region("rectangleregion"))).toBe(false);
  });
});
