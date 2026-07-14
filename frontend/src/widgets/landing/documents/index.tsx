import { DOCUMENTS_DATA, DOCUMENT_SLIDES } from "./data";
import DocumentsHeading from "./ui/heading";
import DocumentsSlider from "./ui/slider";
import styles from "./style.module.scss";

const Documents = () => {
  return (
    <section id="documents" className={styles.section}>
      <div className={styles.inner}>
        <DocumentsHeading
          title={DOCUMENTS_DATA.title}
          subtitle={DOCUMENTS_DATA.subtitle}
        />
        <DocumentsSlider slides={DOCUMENT_SLIDES} />
      </div>
    </section>
  );
};

export default Documents;
