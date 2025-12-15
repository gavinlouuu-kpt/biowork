import { useCallback, useEffect, useRef, useState } from "react";
import { observer } from "mobx-react";

import { IconChevron } from "@humansignal/ui";
import { Button } from "../../common/Button/Button";
import { Block, Elem } from "../../utils/bem";
import { clamp, sortAnnotations } from "../../utils/utilities";
import { AnnotationButton } from "./AnnotationButton";

import "./AnnotationsCarousel.scss";

interface AnnotationsCarouselInterface {
  store: any;
  annotationStore: any;
  commentStore?: any;
}

export const AnnotationsCarousel = observer(({ store, annotationStore }: AnnotationsCarouselInterface) => {
  const [entities, setEntities] = useState<any[]>([]);
  const enableAnnotations = store.hasInterface("annotations:tabs");
  const enablePredictions = store.hasInterface("predictions:tabs");
  const enableCreateAnnotation = store.hasInterface("annotations:add-new");
  const groundTruthEnabled = store.hasInterface("ground-truth");
  const enableAnnotationDelete = store.hasInterface("annotations:delete");
  const carouselRef = useRef<HTMLElement>();
  const containerRef = useRef<HTMLElement>();
  const [currentPosition, setCurrentPosition] = useState(0);
  const [isLeftDisabled, setIsLeftDisabled] = useState(false);
  const [isRightDisabled, setIsRightDisabled] = useState(false);

  const updatePosition = useCallback(
    (e: MouseEvent, goLeft = true) => {
      if (containerRef.current && carouselRef.current) {
        const step = containerRef.current.clientWidth;
        const carouselWidth = carouselRef.current.clientWidth;
        const newPos = clamp(goLeft ? currentPosition - step : currentPosition + step, 0, carouselWidth - step);

        setCurrentPosition(newPos);
      }
    },
    [containerRef, carouselRef, currentPosition],
  );

  useEffect(() => {
    setIsLeftDisabled(currentPosition <= 0);
    setIsRightDisabled(
      currentPosition >= (carouselRef.current?.clientWidth ?? 0) - (containerRef.current?.clientWidth ?? 0),
    );
  }, [
    entities.length,
    containerRef.current,
    carouselRef.current,
    currentPosition,
    window.innerWidth,
    window.innerHeight,
  ]);

  useEffect(() => {
    const newEntities = [];

    if (enablePredictions) newEntities.push(...annotationStore.predictions);

    if (enableAnnotations) newEntities.push(...annotationStore.annotations);
    setEntities(newEntities);
  }, [annotationStore, JSON.stringify(annotationStore.predictions), JSON.stringify(annotationStore.annotations)]);

  return enableAnnotations || enablePredictions || enableCreateAnnotation ? (
    <Block name="annotations-carousel" style={{ "--carousel-left": `${currentPosition}px` }}>
      <Elem ref={containerRef} name="container">
        <Elem ref={carouselRef} name="carosel">
          {sortAnnotations(entities).map((entity) => (
            <AnnotationButton
              key={entity?.id}
              entity={entity}
              capabilities={{
                enablePredictions,
                enableCreateAnnotation,
                groundTruthEnabled,
                enableAnnotations,
                enableAnnotationDelete,
              }}
              annotationStore={annotationStore}
            />
          ))}
          <SegmentationMetricsButton />
        </Elem>
      </Elem>
      {(!isLeftDisabled || !isRightDisabled) && (
        <Elem name="carousel-controls">
          <Elem
            tag={Button}
            name="nav"
            disabled={isLeftDisabled}
            mod={{ left: true, disabled: isLeftDisabled }}
            aria-label="Carousel left"
            onClick={(e: MouseEvent) => !isLeftDisabled && updatePosition(e, true)}
          >
            <Elem name="arrow" mod={{ left: true }} tag={IconChevron} />
          </Elem>
          <Elem
            tag={Button}
            name="nav"
            disabled={isRightDisabled}
            mod={{ right: true, disabled: isRightDisabled }}
            aria-label="Carousel right"
            onClick={(e: MouseEvent) => !isRightDisabled && updatePosition(e, false)}
          >
            <Elem name="arrow" mod={{ right: true }} tag={IconChevron} />
          </Elem>
        </Elem>
      )}
    </Block>
  ) : null;
});

const SegmentationMetricsButton = observer(() => {
  const [active, setActive] = useState(false);

  useEffect(() => {
    const dm: any = (window as any).dataManager;
    if (!dm || typeof dm.on !== "function" || !dm.store) return;

    const updateFromStore = (view?: string) => {
      const current = view ?? dm.store.labelingView;
      setActive(current === "segmentation");
    };

    const handler = (view: string) => {
      updateFromStore(view);
    };

    updateFromStore();

    dm.on("segmentationViewChanged", handler);

    return () => {
      dm.off?.("segmentationViewChanged", handler);
    };
  }, []);

  const handleClick = useCallback(() => {
    const dm: any = (window as any).dataManager;
    if (!dm || !dm.store || typeof dm.store.setLabelingView !== "function") return;

    dm.store.setLabelingView("segmentation");
  }, []);

  const showButton = typeof (window as any).dataManager !== "undefined";

  if (!showButton) return null;

  return (
    <Block name="annotation-button" mod={{ selected: active }}>
      <Elem name="mainSection" onClick={handleClick}>
        <Elem name="main">
          <Elem name="user">
            <Elem tag="span" name="name">
              Segmentation metrics
            </Elem>
          </Elem>
        </Elem>
      </Elem>
    </Block>
  );
});

