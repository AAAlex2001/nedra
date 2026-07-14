import Card from "@/shared/ui/card";
import { GlobeIcon, PdfIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

export type DocLink = {
  label: string;
  kind: "pdf" | "sign";
  href: string;
};

type DocsCardProps = {
  title?: string;
  docs: DocLink[];
};

const DocsCard = ({ title, docs }: DocsCardProps) => (
  <Card tone="soft" gap={20}>
    {title ? <h2 className={styles.title}>{title}</h2> : null}

    <ul className={styles.list}>
      {docs.map((doc) => (
        <li key={`${doc.label}-${doc.kind}`} className={styles.li}>
          <a
            className={styles.item}
            href={doc.href}
            target="_blank"
            rel="noopener noreferrer"
          >
            {doc.kind === "pdf" ? (
              <PdfIcon className={styles.icon} />
            ) : (
              <GlobeIcon className={styles.icon} />
            )}
            <span className={styles.text}>{doc.label}</span>
          </a>
        </li>
      ))}
    </ul>
  </Card>
);

export default DocsCard;
