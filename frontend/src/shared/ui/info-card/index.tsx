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

const isExternal = (href: string) => /^https?:/.test(href);

const InfoCard = ({ rows, children }: InfoCardProps) => (
  <Card gap={0}>
    <dl className={styles.dl}>
      {rows.map((row, index) => (
        <div
          key={index}
          className={`${styles.row} ${index < rows.length - 1 ? styles.divider : ""}`}
        >
          <dt className={styles.label}>{row.label}</dt>
          <dd className={styles.value}>
            {row.href ? (
              <a
                className={styles.link}
                href={row.href}
                {...(isExternal(row.href)
                  ? { target: "_blank", rel: "noopener noreferrer" }
                  : {})}
              >
                {row.value}
              </a>
            ) : (
              row.value
            )}
          </dd>
        </div>
      ))}
    </dl>
    {children}
  </Card>
);

export default InfoCard;
