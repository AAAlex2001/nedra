"use client";

import "keen-slider/keen-slider.min.css";
import { useKeenSlider } from "keen-slider/react";
import { useState } from "react";
import { ArticleCard, type ArticleCardData } from "@/entities/article";
import Button from "@/shared/ui/button";
import styles from "./style.module.scss";

type ArticlesProps = {
  items: ArticleCardData[];
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

const Articles = ({ items }: ArticlesProps) => {
  const [active, setActive] = useState(0);

  const [sliderRef, slider] = useKeenSlider<HTMLDivElement>({
    loop: true,
    slides: { perView: "auto", spacing: 16 },
    slideChanged: (instance) => setActive(instance.track.details.rel),
  });

  return (
    <section className={styles.articles}>
      <div className={styles.panel}>
        <div className={styles.heading}>
          <h2 className={styles.title}>Разбираем экспертизу по шагам</h2>
          <p className={styles.lead}>
            Сроки, штрафы, документы и требования Ростехнадзора — без канцелярита,
            со ссылками на первоисточники.
          </p>
        </div>

        <div ref={sliderRef} className={`keen-slider ${styles.viewport}`}>
          {items.map((item) => (
            <div key={item.slug} className={`keen-slider__slide ${styles.slide}`}>
              <ArticleCard article={item} />
            </div>
          ))}
        </div>
      </div>

      <div className={styles.controls}>
        <div className={styles.dots}>
          {items.map((item, index) => (
            <button
              key={item.slug}
              type="button"
              aria-label={item.title}
              className={`${styles.dot} ${index === active ? styles.dotActive : ""}`}
              onClick={() => slider.current?.moveToIdx(index)}
            />
          ))}
        </div>

        <div className={styles.arrows}>
          <button
            type="button"
            className={styles.button}
            aria-label="Предыдущая статья"
            onClick={() => slider.current?.prev()}
          >
            <Chevron direction="left" />
          </button>
          <button
            type="button"
            className={styles.button}
            aria-label="Следующая статья"
            onClick={() => slider.current?.next()}
          >
            <Chevron direction="right" />
          </button>
        </div>
      </div>

      <Button className={styles.more} href="/novosti">
        Все материалы
      </Button>
    </section>
  );
};

export default Articles;
