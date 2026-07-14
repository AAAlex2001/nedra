import type { CSSProperties, ReactNode } from "react";
import styles from "./style.module.scss";

type CardProps = {
  children: ReactNode;
  tone?: "light" | "soft";
  gap?: number;
};

const Card = ({ children, tone = "light", gap = 20 }: CardProps) => (
  <div
    className={`${styles.card} ${tone === "soft" ? styles.soft : ""}`}
    style={{ gap: `${gap}px` } as CSSProperties}
  >
    {children}
  </div>
);

export default Card;
