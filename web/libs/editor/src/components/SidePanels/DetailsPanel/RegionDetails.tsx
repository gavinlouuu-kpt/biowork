import { observer } from "mobx-react";
import { type FC, useEffect, useMemo, useRef, useState } from "react";
import { Block, Elem, useBEM } from "../../../utils/bem";
import { RegionEditor } from "./RegionEditor";
import "./RegionDetails.scss";
import { Typography } from "@humansignal/ui";
import { decode as rleDecode } from "@thi.ng/rle-pack";

const TextResult: FC<{ mainValue: string[] }> = observer(({ mainValue }) => {
  return (
    <div className="flex flex-col items-start gap-tighter">
      {mainValue.map((value: string, i: number) => (
        <mark
          key={`${value}-${i}`}
          className="bg-primary-background px-tighter py-tightest rounded-sm text-neutral-content"
        >
          <Typography data-counter={i + 1} size="small" className="!m-0">
            {value}
          </Typography>
        </mark>
      ))}
    </div>
  );
});

const ChoicesResult: FC<{ mainValue: string[] }> = observer(({ mainValue }) => {
  return (
    <mark className="bg-primary-background px-tighter py-tightest rounded-sm">
      <Typography as="span" size="small" className="text-neutral-content">
        {mainValue.join(", ")}
      </Typography>
    </mark>
  );
});

const RatingResult: FC<{ mainValue: string[] }> = observer(({ mainValue }) => {
  return <span>{mainValue}</span>;
});

export const ResultItem: FC<{ result: any }> = observer(({ result }) => {
  const { type, mainValue } = result;
  /**
   * @todo before fix this var was always false, so fix is left commented out
   * intention was to don't show per-region textarea text twice —
   * in region list and in region details; it failed but there were no complaints
   */
  // const isRegionList = from_name.displaymode === PER_REGION_MODES.REGION_LIST;

  const content = useMemo(() => {
    if (type === "rating") {
      return (
        <Elem name="result">
          <Typography size="small">Rating: </Typography>
          <Elem name="value">
            <RatingResult mainValue={mainValue} />
          </Elem>
        </Elem>
      );
    }
    if (type === "textarea") {
      return (
        <Elem name="result">
          <Typography size="small">Text: </Typography>
          <Elem name="value">
            <TextResult mainValue={mainValue} />
          </Elem>
        </Elem>
      );
    }
    if (type === "choices") {
      return (
        <Elem name="result">
          <Typography size="small">Choices: </Typography>
          <Elem name="value">
            <ChoicesResult mainValue={mainValue} />
          </Elem>
        </Elem>
      );
    }
    if (type === "taxonomy") {
      return (
        <Elem name="result">
          <Typography size="small">Taxonomy: </Typography>
          <Elem name="value">
            <ChoicesResult mainValue={mainValue.map((v: string[]) => v.join("/"))} />
          </Elem>
        </Elem>
      );
    }
  }, [type, mainValue]);

  return content ? <Block name="region-meta">{content}</Block> : null;
});

export const RegionDetailsMain: FC<{ region: any }> = observer(({ region }) => {
  return (
    <>
      <Elem name="result">
        {(region?.results as any[]).map((res) => (
          <ResultItem key={res.pid} result={res} />
        ))}
        <RegionPixelStats region={region} />
        {region?.text ? (
          <Block name="region-meta">
            <Elem name="item">
              <Elem name="content" mod={{ type: "text" }}>
                {region.text.replace(/\\n/g, "\n")}
              </Elem>
            </Elem>
          </Block>
        ) : null}
      </Elem>
      <RegionEditor region={region} />
    </>
  );
});

type RegionDetailsMetaProps = {
  region: any;
  editMode?: boolean;
  cancelEditMode?: () => void;
  enterEditMode?: () => void;
};

export const RegionDetailsMeta: FC<RegionDetailsMetaProps> = observer(
  ({ region, editMode, cancelEditMode, enterEditMode }) => {
    const bem = useBEM();
    const input = useRef<HTMLTextAreaElement | null>();

    const saveMeta = (value: string) => {
      region.setMetaText(value);
    };

    useEffect(() => {
      if (editMode && input.current) {
        const { current } = input;

        current.focus();
        current.setSelectionRange(current.value.length, current.value.length);
      }
    }, [editMode]);

    return (
      <>
        {editMode ? (
          <textarea
            ref={(el) => (input.current = el)}
            placeholder="Meta"
            className={bem.elem("meta-text").toClassName()}
            value={region.meta.text}
            onChange={(e) => saveMeta(e.target.value)}
            onBlur={(e) => {
              saveMeta(e.target.value);
              cancelEditMode?.();
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                saveMeta(e.target.value);
                cancelEditMode?.();
              }
            }}
          />
        ) : (
          region.meta?.text && (
            <Elem name="meta-text" onClick={() => enterEditMode?.()}>
              {region.meta?.text}
            </Elem>
          )
        )}
      </>
    );
  },
);

/**
 * Compute and display pixel intensity stats (min/mean/max) for brush/bitmask masks
 */
const RegionPixelStats: FC<{ region: any }> = observer(({ region }) => {
  const [stats, setStats] = useState<null | { count: number; min: number; max: number; mean: number }>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadImageAsCanvas(imageEntity: any): Promise<HTMLCanvasElement> {
      const img = new Image();
      // Ensure CORS so we can read pixels
      try {
        const crossOrigin = imageEntity?.imageCrossOrigin ?? "anonymous";
        if (crossOrigin) img.crossOrigin = crossOrigin;
      } catch {}
      img.src = imageEntity?.currentSrc ?? imageEntity?.src;
      await img.decode();

      const canvas = document.createElement("canvas");
      canvas.width = imageEntity?.naturalWidth ?? img.naturalWidth;
      canvas.height = imageEntity?.naturalHeight ?? img.naturalHeight;
      const ctx = canvas.getContext("2d");
      if (!ctx) throw new Error("Canvas 2D not available");
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      return canvas;
    }

    async function loadMaskAsCanvasBrush(): Promise<HTMLCanvasElement | null> {
      const imgModel = region?.object;
      const naturalWidth = imgModel?.currentImageEntity?.naturalWidth;
      const naturalHeight = imgModel?.currentImageEntity?.naturalHeight;
      if (!naturalWidth || !naturalHeight) return null;

      const canvas = document.createElement("canvas");
      canvas.width = naturalWidth;
      canvas.height = naturalHeight;
      const ctx = canvas.getContext("2d");
      if (!ctx) return null;

      // Priority: maskDataURL (from Magic Wand) → RLE → touches
      if (region?.maskDataURL) {
        const maskImg = new Image();
        maskImg.src = region.maskDataURL;
        await maskImg.decode();
        ctx.drawImage(maskImg, 0, 0, naturalWidth, naturalHeight);
        return canvas;
      }

      if (region?.rle && region.rle.length) {
        const data = rleDecode(region.rle);
        const imageData = new ImageData(naturalWidth, naturalHeight);
        // rleDecode returns a Uint8Array RGBA
        imageData.data.set(data);
        ctx.putImageData(imageData, 0, 0);
        return canvas;
      }

      if (Array.isArray(region?.touches) && region.touches.length > 0) {
        // Recreate mask by drawing strokes using relative points onto natural-sized canvas
        ctx.save();
        ctx.fillStyle = "#000";
        ctx.strokeStyle = "#000";
        ctx.lineCap = "round";
        ctx.lineJoin = "round";

        for (const touch of region.touches) {
          const t = typeof touch.toJSON === "function" ? touch.toJSON() : touch;
          const points: number[] = t?.relativePoints ?? t?.points ?? [];
          const type: string = t?.type ?? "add";
          const compositeOperation = type === "eraser" ? "destination-out" : "source-over";
          ctx.globalCompositeOperation = compositeOperation as GlobalCompositeOperation;
          // relativeStrokeWidth is percentage of image width
          const rel = t?.relativeStrokeWidth ?? 0;
          ctx.lineWidth = (rel / 100) * naturalWidth;

          if (points.length >= 2) {
            // Convert relative [x,y] in 0..100 to absolute px
            const toAbs = (x: number, y: number) => [
              (x / 100) * naturalWidth,
              (y / 100) * naturalHeight,
            ] as const;

            ctx.beginPath();
            const [mx, my] = toAbs(points[0], points[1]);
            ctx.moveTo(mx, my);
            for (let i = 0; i < points.length / 2; i++) {
              const [px, py] = toAbs(points[2 * i], points[2 * i + 1]);
              ctx.lineTo(px, py);
            }
            ctx.stroke();
          }
        }
        ctx.restore();
        return canvas;
      }

      return null;
    }

    async function loadMaskAsCanvasBitmask(): Promise<HTMLCanvasElement | null> {
      // Prefer using existing offscreen canvas if available
      const offscreen: any = region?.offscreenCanvasRef;
      const naturalWidth = region?.object?.currentImageEntity?.naturalWidth;
      const naturalHeight = region?.object?.currentImageEntity?.naturalHeight;
      if (offscreen && typeof (offscreen as any).getContext === "function") {
        // Convert OffscreenCanvas to regular canvas for getImageData compatibility
        const canvas = document.createElement("canvas");
        canvas.width = offscreen.width;
        canvas.height = offscreen.height;
        const ctx = canvas.getContext("2d");
        if (!ctx) return null;
        ctx.drawImage(offscreen as any, 0, 0);
        return canvas;
      }
      // Fallback to imageDataURL if present
      if (region?.imageDataURL && naturalWidth && naturalHeight) {
        const canvas = document.createElement("canvas");
        canvas.width = naturalWidth;
        canvas.height = naturalHeight;
        const ctx = canvas.getContext("2d");
        if (!ctx) return null;
        const img = new Image();
        img.src = region.imageDataURL;
        await img.decode();
        ctx.drawImage(img, 0, 0);
        return canvas;
      }
      return null;
    }

    async function compute() {
      setError(null);
      setStats(null);

      const type: string = region?.type ?? "";
      if (!type || (type !== "brushregion" && type !== "bitmaskregion")) return;
      const imageEntity = region?.object?.currentImageEntity ?? region?.object;
      if (!imageEntity) return;

      try {
        const [imageCanvas, maskCanvas] = await Promise.all([
          loadImageAsCanvas(imageEntity),
          type === "bitmaskregion" ? loadMaskAsCanvasBitmask() : loadMaskAsCanvasBrush(),
        ]);

        if (!maskCanvas) return;
        if (cancelled) return;

        const imgCtx = imageCanvas.getContext("2d");
        const maskCtx = maskCanvas.getContext("2d");
        if (!imgCtx || !maskCtx) return;

        // Ensure same dimensions
        const width = imageCanvas.width;
        const height = imageCanvas.height;
        if (maskCanvas.width !== width || maskCanvas.height !== height) {
          // Resample mask to match image
          const resized = document.createElement("canvas");
          resized.width = width;
          resized.height = height;
          const rctx = resized.getContext("2d");
          if (!rctx) return;
          rctx.drawImage(maskCanvas, 0, 0, width, height);
          const maskData = rctx.getImageData(0, 0, width, height);
          const imgData = imgCtx.getImageData(0, 0, width, height);
          const res = calcStats(imgData.data, maskData.data);
          if (!cancelled) setStats(res);
          return;
        }

        const maskData = maskCtx.getImageData(0, 0, width, height);
        const imgData = imgCtx.getImageData(0, 0, width, height);
        const res = calcStats(imgData.data, maskData.data);
        if (!cancelled) setStats(res);
      } catch (e: any) {
        if (!cancelled) setError(e?.message || "Failed to compute stats");
      }
    }

    // Defer heavy work
    const id = (window as any).requestIdleCallback ? (window as any).requestIdleCallback(compute) : setTimeout(compute);
    return () => {
      cancelled = true;
      if ((window as any).cancelIdleCallback) (window as any).cancelIdleCallback(id);
      else clearTimeout(id);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    region?.type,
    region?.rle,
    region?.maskDataURL,
    region?.touches?.length,
    region?.imageDataURL,
    region?.object?.currentImageEntity?.currentSrc,
  ]);

  if (!region || (region.type !== "brushregion" && region.type !== "bitmaskregion")) return null;

  return (
    <Block name="region-meta">
      <Elem name="item">
        <Typography size="small">Pixel intensity</Typography>
        <Elem name="content">
          {error ? (
            <Typography size="small">{error}</Typography>
          ) : stats ? (
            <Typography size="small">
              min: {stats.min.toFixed(1)} max: {stats.max.toFixed(1)} mean: {stats.mean.toFixed(1)} ({stats.count} px)
            </Typography>
          ) : (
            <Typography size="small">Calculating…</Typography>
          )}
        </Elem>
      </Elem>
    </Block>
  );
});

function calcStats(img: Uint8ClampedArray, mask: Uint8ClampedArray) {
  let min = Infinity;
  let max = -Infinity;
  let sum = 0;
  let count = 0;
  // Iterate pixels; img and mask are RGBA
  const total = img.length / 4;
  for (let i = 0; i < total; i++) {
    const mi = i * 4 + 3; // mask alpha
    if (mask[mi] > 0) {
      const base = i * 4;
      const r = img[base];
      const g = img[base + 1];
      const b = img[base + 2];
      const intensity = (r + g + b) / 3; // simple average
      if (intensity < min) min = intensity;
      if (intensity > max) max = intensity;
      sum += intensity;
      count++;
    }
  }
  const mean = count > 0 ? sum / count : 0;
  if (count === 0) {
    min = 0;
    max = 0;
  }
  return { min, max, mean, count };
}
