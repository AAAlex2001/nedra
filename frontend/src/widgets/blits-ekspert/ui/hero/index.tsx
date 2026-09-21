"use client";

import "keen-slider/keen-slider.min.css";
import { useKeenSlider } from "keen-slider/react";
import Image from "next/image";
import { useState, type ReactNode } from "react";
import { HERO, SLIDES } from "../../data";
import styles from "./style.module.scss";

type HeroProps = {
  action: ReactNode;
};

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

const Hero = ({ action }: HeroProps) => {
  const [active, setActive] = useState(0);

  const [sliderRef, slider] = useKeenSlider<HTMLDivElement>({
    loop: true,
    slides: { perView: 1 },
    slideChanged: (instance) => setActive(instance.track.details.rel),
  });

  return (
    <section className={styles.hero}>
      <h1 className={styles.title}>{HERO.title}</h1>
      <p className={styles.lead}>{HERO.text}</p>

      <div className={styles.actions}>{action}</div>

      <div className={styles.slider}>
        <div ref={sliderRef} className={`keen-slider ${styles.viewport}`}>
          {SLIDES.map((slide, index) => (
            <article key={slide.title} className={`keen-slider__slide ${styles.slide}`}>
              <div className={styles.slideText}>
                <h2 className={styles.slideTitle}>{slide.title}</h2>
                <p className={styles.slideLead}>{slide.text}</p>
              </div>

              <Image
                className={styles.slideImage}
                src={slide.image}
                alt={slide.title}
                width={1000}
                height={800}
                sizes="(min-width: 1440px) 420px, (min-width: 768px) 38vw, 70vw"
                priority={index === 0}
              />
            </article>
          ))}
        </div>

        <div className={styles.controls}>
          <div className={styles.dots} role="tablist" aria-label="Слайды">
            {SLIDES.map((slide, index) => (
              <button
                key={slide.title}
                type="button"
                role="tab"
                aria-selected={index === active}
                aria-label={slide.title}
                className={`${styles.dot} ${index === active ? styles.dotActive : ""}`}
                onClick={() => slider.current?.moveToIdx(index)}
              />
            ))}
          </div>

          <div className={styles.arrows}>
            <button
              type="button"
              className={styles.button}
              aria-label="Предыдущий слайд"
              onClick={() => slider.current?.prev()}
            >
              <Chevron direction="left" />
            </button>
            <button
              type="button"
              className={styles.button}
              aria-label="Следующий слайд"
              onClick={() => slider.current?.next()}
            >
              <Chevron direction="right" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
