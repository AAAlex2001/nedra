import classNames from "classnames";
import type { ReactNode } from "react";
import styles from "./style.module.scss";

type DetailsTableProps = {
  children: ReactNode;
};

type DetailsRowProps = {
  label: string;
  action?: ReactNode;
  children: ReactNode;
};

export const DetailsTable = ({ children }: DetailsTableProps) => (
  <dl className={styles.table}>{children}</dl>
);

export const DetailsRow = ({ label, action, children }: DetailsRowProps) => (
  <div className={classNames(styles.row, action && styles.withAction)}>
    <dt className={styles.term}>{label}</dt>
    <dd className={styles.value}>{children}</dd>
    {action && <div className={styles.action}>{action}</div>}
  </div>
);
