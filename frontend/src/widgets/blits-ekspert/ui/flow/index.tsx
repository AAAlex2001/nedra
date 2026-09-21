"use client";

import "keen-slider/keen-slider.min.css";
import { useKeenSlider } from "keen-slider/react";
import Image from "next/image";
import { useState } from "react";
import { STEPS } from "../../data";
import styles from "./style.module.scss";

const Chevron = ({ direction }: { direction: "left" | "right" }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden>
    <path
      d={direction === "left" ? "M14 6L8 12L14 18" : "M10 6L16 12L10 18"}
      stroke="currentColor"
      strokeWidth="2"
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const Flow = () => {
  const [active, setActive] = useState(0);

  const [sliderRef, slider] = useKeenSlider<HTMLDivElement>({
    loop: true,
    slides: { perView: "auto", spacing: 16 },
    slideChanged: (instance) => setActive(instance.track.details.rel),
  });

  return (
    <section className={styles.flow} id="kak-prohodit">
      <div className={styles.heading}>
        <h2 className={styles.title}>Как проходит экспертиза</h2>
        <p className={styles.lead}>
          Девять шагов от загрузки документации до акта выполненных работ.
        </p>
      </div>

      <div ref={sliderRef} className={`keen-slider ${styles.viewport}`}>
        {STEPS.map((step, index) => (
          <article key={step.title} className={`keen-slider__slide ${styles.card}`}>
            <Image
              className={styles.image}
              src={step.image}
              alt={`Экспертиза промышленной безопасности, шаг ${index + 1}: ${step.title}`}
              width={800}
              height={800}
              sizes="(min-width: 1440px) 320px, (min-width: 768px) 40vw, 80vw"
            />
            <span className={styles.number}>Шаг {index + 1}</span>
            <h3 className={styles.cardTitle}>{step.title}</h3>
            <p className={styles.cardText}>{step.text}</p>
          </article>
        ))}
      </div>

      <div className={styles.controls}>
        <div className={styles.dots}>
          {STEPS.map((step, index) => (
            <button
              key={step.title}
              type="button"
              aria-label={step.title}
              className={`${styles.dot} ${index === active ? styles.dotActive : ""}`}
              onClick={() => slider.current?.moveToIdx(index)}
            />
          ))}
        </div>

        <div className={styles.arrows}>
          <button
            type="button"
            className={styles.button}
            aria-label="Предыдущий шаг"
            onClick={() => slider.current?.prev()}
          >
            <Chevron direction="left" />
          </button>
          <button
            type="button"
            className={styles.button}
            aria-label="Следующий шаг"
            onClick={() => slider.current?.next()}
          >
            <Chevron direction="right" />
          </button>
        </div>
      </div>
    </section>
  );
};

export default Flow;
