"use client";

import type { ReactNode } from "react";
import { useStickyTop } from "../../model/use-sticky-top";

type StickyAsideProps = {
  className: string;
  children: ReactNode;
};

const StickyAside = ({ className, children }: StickyAsideProps) => {
  const { ref, top, maxHeight } = useStickyTop();

  return (
    <aside ref={ref} className={className} style={{ top, maxHeight }}>
      {children}
    </aside>
  );
};

export default StickyAside;
