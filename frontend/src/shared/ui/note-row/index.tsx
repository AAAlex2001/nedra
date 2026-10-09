import classNames from "classnames";
import type { ReactNode } from "react";
import styles from "./style.module.scss";

type NoteRowProps = {
  icon: ReactNode;
  children: ReactNode;
  divider?: boolean;
};

const NoteRow = ({ icon, children, divider = false }: NoteRowProps) => (
  <div className={classNames(styles.note, divider && styles.divider)}>
    <span className={styles.icon}>{icon}</span>
    <p className={styles.text}>{children}</p>
  </div>
);

export default NoteRow;
