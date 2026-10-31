"use client";

import type { ReactNode } from "react";
import { useStickyTop } from "../../model/use-sticky-top";

type StickyAsideProps = {
  className: string;
  children: ReactNode;
};

const StickyAside = ({ className, children }: StickyAsideProps) => {
  const { ref, top } = useStickyTop();

  return (
    <aside ref={ref} className={className} style={{ top }}>
      {children}
    </aside>
  );
};

export default StickyAside;
