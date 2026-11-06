"use client";

import "keen-slider/keen-slider.min.css";
import { useKeenSlider } from "keen-slider/react";
import { Children, useState, type ReactNode } from "react";
import SliderControls from "@/shared/ui/slider-controls";
import styles from "./style.module.scss";

type ServiceSliderProps = {
  children: ReactNode;
  count: number;
  title: string;
};

const ServiceSlider = ({ children, count, title }: ServiceSliderProps) => {
  const [active, setActive] = useState(0);
  const [sliderRef, slider] = useKeenSlider<HTMLDivElement>({
    mode: "snap",
    slides: { perView: 1, spacing: 20 },
    slideChanged(instance) {
      setActive(instance.track.details.rel);
    },
  });

  return (
    <div className={styles.slider} role="region" aria-label={`Услуги: ${title}`}>
      {count > 1 && (
        <div className={styles.controls}>
          <span aria-live="polite">{active + 1} / {count}</span>
          <SliderControls
            previousLabel="Предыдущая услуга"
            nextLabel="Следующая услуга"
            previousDisabled={active === 0}
            nextDisabled={active === count - 1}
            onPrevious={() => slider.current?.prev()}
            onNext={() => slider.current?.next()}
          />
        </div>
      )}

      <div ref={sliderRef} className={`keen-slider ${styles.track}`}>
        {Children.map(children, child => (
          <div className={`keen-slider__slide ${styles.slide}`}>{child}</div>
        ))}
      </div>
    </div>
  );
};

export default ServiceSlider;
