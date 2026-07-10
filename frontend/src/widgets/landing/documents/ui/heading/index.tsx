import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type DocumentsHeadingProps = {
  title: string;
  subtitle: string;
};

const DocumentsHeading = ({ title, subtitle }: DocumentsHeadingProps) => (
  <div className={styles.heading}>
    <h2 className={styles.title}>{title}</h2>
    <AccentLine width={150} />
    <p className={styles.subtitle}>{subtitle}</p>
  </div>
);

export default DocumentsHeading;
