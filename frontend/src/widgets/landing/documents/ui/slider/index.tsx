"use client";

import "keen-slider/keen-slider.min.css";
import { useKeenSlider } from "keen-slider/react";
import { useState } from "react";
import Lightbox from "@/shared/ui/lightbox";
import styles from "./style.module.scss";

type DocumentsSliderProps = {
  slides: string[];
};

const DocumentsSlider = ({ slides }: DocumentsSliderProps) => {
  const initialSlide = Math.min(2, slides.length - 1);
  const [activeIndex, setActiveIndex] = useState(initialSlide);
  const [lightboxSrc, setLightboxSrc] = useState<string | null>(null);

  const [sliderRef, slider] = useKeenSlider<HTMLDivElement>({
    loop: true,
    initial: initialSlide,
    mode: "snap",
    slides: {
      origin: "center",
      perView: "auto",
      spacing: 30,
    },
    breakpoints: {
      "(min-width: 768px)": {
        slides: {
          origin: "center",
          perView: "auto",
          spacing: 85,
        },
      },
    },
    created(instance) {
      setActiveIndex(instance.track.details.rel);
    },
    slideChanged(instance) {
      setActiveIndex(instance.track.details.rel);
    },
  });

  return (
    <div className={styles.wrap}>
      <div ref={sliderRef} className={`keen-slider ${styles.viewport}`}>
        {slides.map((src, index) => (
          <div
            key={src}
            className={`keen-slider__slide ${styles.slide} ${
              index === activeIndex ? styles.slideActive : ""
            }`}
          >
            <img
              className={styles.image}
              src={src}
              alt={`Документ ${index + 1}`}
              draggable={false}
              onClick={() => setLightboxSrc(src)}
            />
          </div>
        ))}
      </div>

      <div className={styles.controls}>
        <button
          type="button"
          className={styles.button}
          aria-label="Предыдущий документ"
          onClick={() => slider.current?.prev()}
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
          onClick={() => slider.current?.next()}
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

      {lightboxSrc && (
        <Lightbox src={lightboxSrc} onClose={() => setLightboxSrc(null)} />
      )}
    </div>
  );
};

export default DocumentsSlider;
