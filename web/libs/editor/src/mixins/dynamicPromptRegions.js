const PROMPT_REGION_TYPES = new Set(["keypointregion", "rectangleregion"]);

export const isPromptRegionType = (type) => PROMPT_REGION_TYPES.has(type);

export const isConnectedDynamicRegion = (sourceRegion, candidateRegion) => {
  const sourceIsPromptRegion = isPromptRegionType(sourceRegion.type);
  const candidateIsPromptRegion = isPromptRegionType(candidateRegion.type);
  const sameRegionType = sourceIsPromptRegion ? candidateIsPromptRegion : candidateRegion.type === sourceRegion.type;
  const activePromptCandidate = !sourceIsPromptRegion || !candidateIsPromptRegion || candidateRegion.dynamic;

  return (
    sameRegionType &&
    activePromptCandidate &&
    candidateRegion.labelName === sourceRegion.labelName &&
    candidateRegion.results?.[0]?.to_name === sourceRegion.results?.[0]?.to_name
  );
};
