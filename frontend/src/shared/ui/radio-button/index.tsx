import type { ReactNode } from "react";
import styles from "./style.module.scss";

type RadioButtonProps = {
  checked: boolean;
  label: ReactNode;
  onSelect: () => void;
  className?: string;
};

const RadioButton = ({ checked, label, onSelect, className }: RadioButtonProps) => (
  <button
    type="button"
    role="radio"
    aria-checked={checked}
    onClick={onSelect}
    className={`${styles.option} ${checked ? styles.checked : ""} ${className ?? ""}`}
  >
    <span className={styles.indicator} aria-hidden="true">
      {checked && <span className={styles.dot} />}
    </span>
    <span className={styles.label}>{label}</span>
  </button>
);

export default RadioButton;
