import type { ReactNode } from "react";
import styles from "./style.module.scss";

type ChipProps = {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
  disabled?: boolean;
  title?: string;
};

const Chip = ({ active, onClick, children, disabled, title }: ChipProps) => (
  <button
    type="button"
    role="checkbox"
    aria-checked={active}
    title={title}
    disabled={disabled}
    className={`${styles.chip} ${active ? styles.active : ""}`}
    onClick={onClick}
  >
    {children}
  </button>
);

export default Chip;
