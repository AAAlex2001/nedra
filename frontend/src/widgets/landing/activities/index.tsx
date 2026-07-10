import { ACTIVITIES_DATA, FEATURE_ITEMS, METHODOLOGY_CARD } from "./data";
import ActivitiesContent from "./ui/content";
import styles from "./style.module.scss";

const Activities = () => {
  return (
    <section className={styles.section}>
      <div className={styles.image} aria-hidden />
      <div className={styles.overlay} aria-hidden />
      <ActivitiesContent
        heading={ACTIVITIES_DATA}
        features={FEATURE_ITEMS}
        card={METHODOLOGY_CARD}
      />
    </section>
  );
};

export default Activities;
