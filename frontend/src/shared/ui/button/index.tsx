import Link from "next/link";
import type { ReactNode } from "react";
import styles from "./style.module.scss";

type ButtonProps = {
  children: ReactNode;
  type?: "button" | "submit";
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
  href?: string;
  scroll?: boolean;
};

const Button = ({
  children,
  type = "button",
  disabled,
  onClick,
  className,
  href,
  scroll = true,
}: ButtonProps) => {
  if (href) {
    return (
      <Link href={href} scroll={scroll} className={`${styles.button} ${className ?? ""}`}>
        <span className={styles.text}>{children}</span>
      </Link>
    );
  }

  return (
    <button
      type={type}
      className={`${styles.button} ${className ?? ""}`}
      disabled={disabled}
      onClick={onClick}
    >
      <span className={styles.text}>{children}</span>
    </button>
  );
};

export default Button;
