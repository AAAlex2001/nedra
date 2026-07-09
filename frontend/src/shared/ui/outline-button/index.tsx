import Link from "next/link";
import type { ReactNode } from "react";
import styles from "./style.module.scss";

type OutlineButtonProps = {
  href: string;
  children: ReactNode;
  className?: string;
};

const OutlineButton = ({ href, children, className }: OutlineButtonProps) => {
  return (
    <Link className={`${styles.button} ${className ?? ""}`} href={href}>
      <span className={styles.text}>{children}</span>
    </Link>
  );
};

export default OutlineButton;
