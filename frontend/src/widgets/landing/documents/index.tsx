import DocumentsHeading from "./ui/heading";
import DocumentsSlider from "./ui/slider";
import styles from "./style.module.scss";

const Documents = () => {
  return (
    <section className={styles.section}>
      <div className={styles.inner}>
        <DocumentsHeading />
        <DocumentsSlider />
      </div>
    </section>
  );
};

export default Documents;
