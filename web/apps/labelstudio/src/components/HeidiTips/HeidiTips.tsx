import { type FC, memo } from "react";
import { FF_HIDE_HEIDI_TIPS, isFF } from "../../utils/feature-flags";
import type { HeidiTipsProps } from "./types";
import { HeidiTip } from "./HeidiTip";
import { useRandomTip } from "./hooks";

export const HeidiTips: FC<HeidiTipsProps> = memo(({ collection }) => {
  if (isFF(FF_HIDE_HEIDI_TIPS)) return null;
  const [tip, dismiss, onLinkClick] = useRandomTip(collection);

  return tip && <HeidiTip tip={tip} onDismiss={dismiss} onLinkClick={onLinkClick} />;
});
