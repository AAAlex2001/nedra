"use client";

import { useRef, useState } from "react";
import { COMPARE_SLIDER } from "./data";
import styles from "./style.module.scss";

const CompareSlider = () => {
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
      <img
        className={styles.image}
        src={COMPARE_SLIDER.beforeImage}
        alt="Состояние объекта до реставрации"
        draggable={false}
      />

      <div
        className={styles.afterLayer}
        style={{ clipPath: `inset(0 0 0 ${position}%)` }}
      >
        <img
          className={styles.image}
          src={COMPARE_SLIDER.afterImage}
          alt="Состояние объекта после реставрации"
          draggable={false}
        />
      </div>

      <span className={styles.chipBefore}>{COMPARE_SLIDER.beforeLabel}</span>
      <span className={styles.chipAfter}>{COMPARE_SLIDER.afterLabel}</span>

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
