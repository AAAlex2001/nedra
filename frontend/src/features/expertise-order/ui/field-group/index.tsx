import type { ReactNode } from "react";
import styles from "./style.module.scss";

type FieldGroupProps = {
  label?: string;
  note?: ReactNode;
  children: ReactNode;
};

const FieldGroup = ({ label, note, children }: FieldGroupProps) => (
  <div className={styles.group}>
    {label && <span className={styles.label}>{label}</span>}
    {children}
    {note && <p className={styles.note}>{note}</p>}
  </div>
);

export default FieldGroup;
