import Link from "next/link";
import type { ReactNode } from "react";
import styles from "./style.module.scss";

type OutlineButtonProps = {
  children: ReactNode;
  href?: string;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
};

const OutlineButton = ({ href, children, onClick, disabled, className }: OutlineButtonProps) => {
  if (href) {
    return (
      <Link className={`${styles.button} ${className ?? ""}`} href={href}>
        <span className={styles.text}>{children}</span>
      </Link>
    );
  }

  return (
    <button
      type="button"
      className={`${styles.button} ${className ?? ""}`}
      disabled={disabled}
      onClick={onClick}
    >
      <span className={styles.text}>{children}</span>
    </button>
  );
};

export default OutlineButton;
