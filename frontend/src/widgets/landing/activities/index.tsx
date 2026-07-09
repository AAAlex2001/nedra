import ActivitiesContent from "./ui/content";
import styles from "./style.module.scss";

const Activities = () => {
  return (
    <section className={styles.section}>
      <div className={styles.image} aria-hidden />
      <div className={styles.overlay} aria-hidden />
      <ActivitiesContent />
    </section>
  );
};

export default Activities;
