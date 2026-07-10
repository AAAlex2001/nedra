import AccentLine from "@/shared/ui/accent-line";
import { DOCUMENTS_DATA } from "../../data";
import styles from "./style.module.scss";

const DocumentsHeading = () => {
  return (
    <div className={styles.heading}>
      <h2 className={styles.title}>{DOCUMENTS_DATA.title}</h2>
      <AccentLine width={150} />
      <p className={styles.subtitle}>{DOCUMENTS_DATA.subtitle}</p>
    </div>
  );
};

export default DocumentsHeading;
