"use client";

import "keen-slider/keen-slider.min.css";
import { useKeenSlider } from "keen-slider/react";
import type { ArticleCard as ArticleCardType } from "../../model/types";
import ArticleCard from "../article-card";
import styles from "./style.module.scss";

type ArticlesSliderProps = {
  articles: ArticleCardType[];
  title?: string;
  ariaLabel: string;
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

const ArticlesSlider = ({ articles, title, ariaLabel }: ArticlesSliderProps) => {
  const [sliderRef, slider] = useKeenSlider<HTMLDivElement>({
    mode: "snap",
    slides: { perView: 1.1, spacing: 16 },
    breakpoints: {
      "(min-width: 768px)": { slides: { perView: 2.2, spacing: 20 } },
      "(min-width: 1440px)": { slides: { perView: 3, spacing: 30 } },
    },
  });

  return (
    <section className={styles.section} aria-label={ariaLabel}>
      <div className={`${styles.head} ${title ? "" : styles.headControlsOnly}`}>
        {title && <h2 className={styles.title}>{title}</h2>}

        <div className={styles.controls}>
          <button
            type="button"
            className={styles.button}
            aria-label="Предыдущие статьи"
            onClick={() => slider.current?.prev()}
          >
            <Chevron direction="left" />
          </button>
          <button
            type="button"
            className={styles.button}
            aria-label="Следующие статьи"
            onClick={() => slider.current?.next()}
          >
            <Chevron direction="right" />
          </button>
        </div>
      </div>

      <div ref={sliderRef} className={`keen-slider ${styles.viewport}`}>
        {articles.map((article) => (
          <div key={article.slug} className={`keen-slider__slide ${styles.slide}`}>
            <ArticleCard article={article} />
          </div>
        ))}
      </div>
    </section>
  );
};

export default ArticlesSlider;
