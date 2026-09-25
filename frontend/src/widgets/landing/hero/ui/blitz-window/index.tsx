"use client";

import "keen-slider/keen-slider.min.css";
import { useKeenSlider, type KeenSliderInstance } from "keen-slider/react";
import Image from "next/image";
import { useState } from "react";
import Button from "@/shared/ui/button";
import { BLITZ_ADVANTAGES, BLITZ_STEPS } from "../../data";
import styles from "./style.module.scss";

const followContainerWidth = (slider: KeenSliderInstance) => {
  const observer = new ResizeObserver(() => slider.update());

  slider.on("created", () => observer.observe(slider.container));
  slider.on("destroyed", () => observer.disconnect());
};

const Chevron = ({ direction }: { direction: "left" | "right" }) => (
  <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden>
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

const BlitzWindow = () => {
  const [active, setActive] = useState(0);

  const [sliderRef, slider] = useKeenSlider<HTMLDivElement>(
    {
      loop: true,
      slides: { perView: 1 },
      slideChanged: (instance) => setActive(instance.track.details.rel),
    },
    [followContainerWidth],
  );

  return (
    <div className={styles.window}>
      <div className={styles.head}>
        <span className={styles.badge}>Блиц-эксперт</span>
        <p className={styles.tagline}>Онлайн экспертиза промышленной безопасности</p>
      </div>

      <div ref={sliderRef} className={`keen-slider ${styles.viewport}`}>
        {BLITZ_STEPS.map((step, index) => (
          <article key={step.title} className={`keen-slider__slide ${styles.slide}`}>
            <Image
              className={styles.image}
              src={step.image}
              alt={step.title}
              width={400}
              height={400}
              sizes="(min-width: 768px) 190px, 120px"
            />
            <div className={styles.slideText}>
              <span className={styles.number}>
                Шаг {index + 1} из {BLITZ_STEPS.length}
              </span>
              <p className={styles.slideTitle}>{step.title}</p>
              <p className={styles.slideLead}>{step.text}</p>
            </div>
          </article>
        ))}
      </div>

      <div className={styles.controls}>
        <div className={styles.dots} role="tablist" aria-label="Шаги экспертизы">
          {BLITZ_STEPS.map((step, index) => (
            <button
              key={step.title}
              type="button"
              role="tab"
              aria-selected={index === active}
              aria-label={step.title}
              className={`${styles.dot} ${index === active ? styles.dotActive : ""}`}
              onClick={() => slider.current?.moveToIdx(index)}
            />
          ))}
        </div>

        <div className={styles.arrows}>
          <button
            type="button"
            className={styles.arrow}
            aria-label="Предыдущий шаг"
            onClick={() => slider.current?.prev()}
          >
            <Chevron direction="left" />
          </button>
          <button
            type="button"
            className={styles.arrow}
            aria-label="Следующий шаг"
            onClick={() => slider.current?.next()}
          >
            <Chevron direction="right" />
          </button>
        </div>
      </div>

      <ul className={styles.advantages}>
        {BLITZ_ADVANTAGES.map((item) => (
          <li key={item.title} className={styles.advantage}>
            <Image
              className={styles.advantageImage}
              src={item.image}
              alt=""
              width={120}
              height={120}
              sizes="56px"
            />
            <span className={styles.advantageText}>
              <span className={styles.advantageTitle}>{item.title}</span>
              <span className={styles.advantageHint}>{item.text}</span>
            </span>
          </li>
        ))}
      </ul>

      <Button href="/blits-ekspert" className={styles.cta}>
        Загрузить документацию
      </Button>
    </div>
  );
};

export default BlitzWindow;
