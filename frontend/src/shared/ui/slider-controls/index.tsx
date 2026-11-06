"use client";

import { ChevronIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type SliderControlsProps = {
  onPrevious: () => void;
  onNext: () => void;
  previousLabel: string;
  nextLabel: string;
  previousDisabled?: boolean;
  nextDisabled?: boolean;
};

const SliderControls = ({
  onPrevious,
  onNext,
  previousLabel,
  nextLabel,
  previousDisabled,
  nextDisabled,
}: SliderControlsProps) => (
  <div className={styles.controls}>
    <button
      type="button"
      className={styles.button}
      aria-label={previousLabel}
      disabled={previousDisabled}
      onClick={onPrevious}
    >
      <ChevronIcon className={styles.previous} />
    </button>
    <button
      type="button"
      className={styles.button}
      aria-label={nextLabel}
      disabled={nextDisabled}
      onClick={onNext}
    >
      <ChevronIcon className={styles.next} />
    </button>
  </div>
);

export default SliderControls;
