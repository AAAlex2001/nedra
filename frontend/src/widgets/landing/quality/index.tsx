import { QUALITY_DATA } from "./data";
import styles from "./style.module.scss";

const Quality = () => {
  return (
    <section className={styles.block}>
      <div className={styles.image} role="img" aria-hidden />
      <div className={styles.overlay} aria-hidden />

      <div className={styles.content}>
        <div className={styles.heading}>
          <h2 className={styles.titleLine1}>{QUALITY_DATA.line1}</h2>
          <p className={styles.titleLine2}>{QUALITY_DATA.line2}</p>
          <p className={styles.titleLine3}>{QUALITY_DATA.line3}</p>
        </div>
      </div>
    </section>
  );
};

export default Quality;
