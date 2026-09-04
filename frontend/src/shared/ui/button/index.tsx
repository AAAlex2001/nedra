import type { ReactNode } from "react";
import styles from "./style.module.scss";

type ButtonProps = {
  children: ReactNode;
  type?: "button" | "submit";
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
};

const Button = ({
  children,
  type = "button",
  disabled,
  onClick,
  className,
}: ButtonProps) => (
  <button
    type={type}
    className={`${styles.button} ${className ?? ""}`}
    disabled={disabled}
    onClick={onClick}
  >
    <span className={styles.text}>{children}</span>
  </button>
);

export default Button;
