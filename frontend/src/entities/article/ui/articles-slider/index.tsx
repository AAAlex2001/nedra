"use client";

import classNames from "classnames";
import "keen-slider/keen-slider.min.css";
import { useKeenSlider } from "keen-slider/react";
import type { ArticleCard as ArticleCardType } from "../../model/types";
import ArticleCard from "../article-card";
import SliderControls from "@/shared/ui/slider-controls";
import styles from "./style.module.scss";

type ArticlesSliderProps = {
  articles: ArticleCardType[];
  title?: string;
  ariaLabel: string;
};

const ArticlesSlider = ({ articles, title, ariaLabel }: ArticlesSliderProps) => {
  const [sliderRef, slider] = useKeenSlider<HTMLDivElement>({
    mode: "snap",
    slides: { perView: 1.5, spacing: 12 },
    breakpoints: {
      "(min-width: 768px)": { slides: { perView: 2.2, spacing: 20 } },
      "(min-width: 1440px)": { slides: { perView: 4, spacing: 24 } },
    },
  });

  return (
    <section className={styles.section} aria-label={ariaLabel}>
      <div className={classNames(styles.head, !title && styles.headControlsOnly)}>
        {title && <h2 className={styles.title}>{title}</h2>}

        <SliderControls
          previousLabel="Предыдущие статьи"
          nextLabel="Следующие статьи"
          onPrevious={() => slider.current?.prev()}
          onNext={() => slider.current?.next()}
        />
      </div>

      <div ref={sliderRef} className={classNames("keen-slider", styles.viewport)}>
        {articles.map((article) => (
          <div key={article.slug} className={classNames("keen-slider__slide", styles.slide)}>
            <ArticleCard article={article} compact />
          </div>
        ))}
      </div>
    </section>
  );
};

export default ArticlesSlider;
