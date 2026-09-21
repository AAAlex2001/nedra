import type { ReactNode } from "react";
import { DocumentIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type DocumentItem = {
  key: string;
  title: string;
  meta: string;
  amount: string;
  href: string;
  status?: ReactNode;
  action?: ReactNode;
};

type DocumentListProps = {
  items: DocumentItem[];
};

const DocumentList = ({ items }: DocumentListProps) => (
  <ul className={styles.list}>
    {items.map((item) => (
      <li key={item.key} className={styles.item}>
        <span className={styles.tile}>
          <DocumentIcon className={styles.icon} />
        </span>

        <div className={styles.body}>
          <p className={styles.title}>{item.title}</p>
          <p className={styles.meta}>{item.meta}</p>
        </div>

        <div className={styles.side}>
          <span className={styles.amount}>{item.amount}</span>
          {item.status}
        </div>

        <div className={styles.actions}>
          <a className={styles.download} href={item.href} target="_blank" rel="noreferrer">
            Скачать PDF
          </a>
          {item.action}
        </div>
      </li>
    ))}
  </ul>
);

export default DocumentList;
