"use client";

import Image from "next/image";
import { useRef, useState } from "react";
import type { CompareSliderData } from "../../data";
import styles from "./style.module.scss";

type CompareSliderProps = {
  data: CompareSliderData;
};

const CompareSlider = ({ data }: CompareSliderProps) => {
  const boxRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState(50);
  const [dragging, setDragging] = useState(false);

  const setPositionByX = (clientX: number) => {
    const box = boxRef.current;
    if (!box) return;

    const rect = box.getBoundingClientRect();
    const percent = ((clientX - rect.left) / rect.width) * 100;

    if (percent < 0) setPosition(0);
    else if (percent > 100) setPosition(100);
    else setPosition(percent);
  };

  return (
    <div
      ref={boxRef}
      className={styles.slider}
      onMouseDown={(event) => {
        setDragging(true);
        setPositionByX(event.clientX);
      }}
      onMouseMove={(event) => {
        if (!dragging) return;
        setPositionByX(event.clientX);
      }}
      onMouseUp={() => setDragging(false)}
      onMouseLeave={() => setDragging(false)}
    >
      <Image
        className={styles.image}
        src={data.beforeImage}
        alt="Состояние объекта до реставрации"
        fill
        sizes="(min-width: 768px) 639px, calc(100vw - 40px)"
        quality={82}
        loading="lazy"
        decoding="async"
        draggable={false}
      />

      <div
        className={styles.afterLayer}
        style={{ clipPath: `inset(0 0 0 ${position}%)` }}
      >
        <Image
          className={styles.image}
          src={data.afterImage}
          alt="Состояние объекта после реставрации"
          fill
          sizes="(min-width: 768px) 639px, calc(100vw - 40px)"
          quality={82}
          loading="lazy"
          decoding="async"
          draggable={false}
        />
      </div>

      <span className={styles.chipBefore}>{data.beforeLabel}</span>
      <span className={styles.chipAfter}>{data.afterLabel}</span>

      <div className={styles.divider} style={{ left: `${position}%` }}>
        <span className={styles.handle}>
          <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden>
            <path d="M7.5 2L3.5 6L7.5 10" stroke="#1E1E1E" strokeWidth="1.5" />
          </svg>
          <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden>
            <path d="M4.5 2L8.5 6L4.5 10" stroke="#1E1E1E" strokeWidth="1.5" />
          </svg>
        </span>
      </div>
    </div>
  );
};

export default CompareSlider;
