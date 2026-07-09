"use client";

import "keen-slider/keen-slider.min.css";
import { useKeenSlider } from "keen-slider/react";
import { useState } from "react";
import { DOCUMENT_SLIDES } from "./data";
import styles from "./style.module.scss";

const SLOT_OFFSETS = [-2, -1, 0, 1, 2] as const;

const DocumentsSlider = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [direction, setDirection] = useState<"prev" | "next" | null>(null);

  const [engineRef, slider] = useKeenSlider({
    loop: true,
    defaultAnimation: {
      duration: 600,
    },
    slides: {
      perView: 1,
    },
    created(instance) {
      setActiveIndex(instance.track.details.rel);
    },
    slideChanged(instance) {
      setActiveIndex(instance.track.details.rel);
      setDirection(null);
    },
  });

  const getSlideIndex = (offset: number) => {
    const length = DOCUMENT_SLIDES.length;
    return ((activeIndex + offset) % length + length) % length;
  };

  const goPrev = () => {
    setDirection("prev");
    slider.current?.prev();
  };

  const goNext = () => {
    setDirection("next");
    slider.current?.next();
  };

  return (
    <div className={styles.wrap}>
      <div
        ref={engineRef}
        className={`keen-slider ${styles.engine}`}
        aria-hidden
      >
        {DOCUMENT_SLIDES.map((src) => (
          <div key={src} className="keen-slider__slide">
            <span />
          </div>
        ))}
      </div>

      <div
        className={`${styles.viewport} ${
          direction === "next"
            ? styles.viewportNext
            : direction === "prev"
              ? styles.viewportPrev
              : ""
        }`}
      >
        {SLOT_OFFSETS.map((offset) => {
          const slideIndex = getSlideIndex(offset);
          const isCenter = offset === 0;

          return (
            <div
              key={offset}
              className={`${styles.slot} ${isCenter ? styles.slotCenter : ""}`}
            >
              <img
                className={styles.image}
                src={DOCUMENT_SLIDES[slideIndex]}
                alt={`Документ ${slideIndex + 1}`}
                draggable={false}
              />
            </div>
          );
        })}
      </div>

      <div className={styles.controls}>
        <button
          type="button"
          className={styles.button}
          aria-label="Предыдущий документ"
          onClick={goPrev}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden>
            <path
              d="M14 6L8 12L14 18"
              stroke="currentColor"
              strokeWidth="2"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        <button
          type="button"
          className={styles.button}
          aria-label="Следующий документ"
          onClick={goNext}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden>
            <path
              d="M10 6L16 12L10 18"
              stroke="currentColor"
              strokeWidth="2"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default DocumentsSlider;
