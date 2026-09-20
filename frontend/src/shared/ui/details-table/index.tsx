import type { ReactNode } from "react";
import styles from "./style.module.scss";

type DetailsTableProps = {
  children: ReactNode;
};

type DetailsRowProps = {
  label: string;
  children: ReactNode;
};

export const DetailsTable = ({ children }: DetailsTableProps) => (
  <dl className={styles.table}>{children}</dl>
);

export const DetailsRow = ({ label, children }: DetailsRowProps) => (
  <div className={styles.row}>
    <dt className={styles.term}>{label}</dt>
    <dd className={styles.value}>{children}</dd>
  </div>
);
