import type { ReactNode } from "react";
import Card from "@/shared/ui/card";
import styles from "./style.module.scss";

export type InfoRow = {
  label: string;
  value: string;
  href?: string;
};

type InfoCardProps = {
  rows: InfoRow[];
  children?: ReactNode;
};

const InfoCard = ({ rows, children }: InfoCardProps) => (
  <Card gap={0}>
    {rows.map((row, index) => (
      <div
        key={index}
        className={`${styles.row} ${index < rows.length - 1 ? styles.divider : ""}`}
      >
        <span className={styles.label}>{row.label}</span>
        {row.href ? (
          <a className={styles.link} href={row.href}>
            {row.value}
          </a>
        ) : (
          <span className={styles.value}>{row.value}</span>
        )}
      </div>
    ))}
    {children}
  </Card>
);

export default InfoCard;
