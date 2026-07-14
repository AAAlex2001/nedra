import Card from "@/shared/ui/card";
import DocsCard from "@/shared/ui/docs-card";
import { GraduationIcon, InfoIcon } from "@/shared/ui/icons";
import SectionHeading from "@/shared/ui/section-heading";
import { OBRAZOVANIE } from "./data";
import styles from "./style.module.scss";

const SvedeniyaObrazovanie = () => {
  const { title, notice, qualification, docsTitle, docs } = OBRAZOVANIE;

  return (
    <>
      <SectionHeading title={title} />

      <Card gap={10}>
        <div className={styles.note}>
          <InfoIcon className={styles.noteIconInfo} />
          <p className={styles.noteText}>{notice}</p>
        </div>
        <div className={styles.note}>
          <GraduationIcon className={styles.noteIcon} />
          <p className={styles.noteText}>{qualification}</p>
        </div>
      </Card>

      <DocsCard title={docsTitle} docs={docs} />
    </>
  );
};

export default SvedeniyaObrazovanie;
