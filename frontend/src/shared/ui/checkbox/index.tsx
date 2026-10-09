import type { ReactNode } from "react";
import styles from "./style.module.scss";

type CheckboxProps = {
  checked?: boolean;
  required?: boolean;
  onChange?: (checked: boolean) => void;
  children: ReactNode;
};

const Checkbox = ({ checked, required, onChange, children }: CheckboxProps) => (
  <label className={styles.checkbox}>
    <input
      type="checkbox"
      className={styles.input}
      checked={checked}
      required={required}
      onChange={(event) => onChange?.(event.target.checked)}
    />
    <span className={styles.box} aria-hidden="true">
      <svg className={styles.mark} viewBox="0 0 16 16" fill="none">
        <path
          d="M3.5 8.5L6.5 11.5L12.5 5"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </span>
    <span className={styles.label}>{children}</span>
  </label>
);

export default Checkbox;
