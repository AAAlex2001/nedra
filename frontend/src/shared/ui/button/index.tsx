import Link from "next/link";
import type { ReactNode } from "react";
import Spinner from "@/shared/ui/spinner";
import styles from "./style.module.scss";

type ButtonProps = {
  children: ReactNode;
  type?: "button" | "submit";
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  className?: string;
  href?: string;
  scroll?: boolean;
};

const Button = ({
  children,
  type = "button",
  disabled,
  loading,
  onClick,
  className,
  href,
  scroll = true,
}: ButtonProps) => {
  if (href) {
    return (
      <Link
        href={href}
        scroll={scroll}
        onClick={onClick}
        className={`${styles.button} ${className ?? ""}`}
      >
        <span className={styles.text}>{children}</span>
      </Link>
    );
  }

  return (
    <button
      type={type}
      className={`${styles.button} ${loading ? styles.loading : ""} ${className ?? ""}`}
      disabled={disabled || loading}
      onClick={onClick}
    >
      <span className={styles.text}>{children}</span>
      {loading && (
        <span className={styles.spinner}>
          <Spinner size={18} tone="light" />
        </span>
      )}
    </button>
  );
};

export default Button;
