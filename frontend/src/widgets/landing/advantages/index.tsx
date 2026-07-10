import AccentLine from "@/shared/ui/accent-line";
import { ADVANTAGES_DATA, ADVANTAGE_CARDS } from "./data";
import styles from "./style.module.scss";

const Advantages = () => {
  return (
    <section className={styles.section}>
      <div className={styles.image} role="img" aria-hidden />
      <div className={styles.overlay} aria-hidden />

      <div className={styles.content}>
        <div className={styles.heading}>
          <h2 className={styles.title}>{ADVANTAGES_DATA.title}</h2>
          <AccentLine width={150} />
        </div>

        <div className={styles.row}>
          {ADVANTAGE_CARDS.map((item) => (
            <article key={item.number} className={styles.card}>
              <span className={styles.number}>{item.number}</span>
              <p className={styles.text}>{item.text}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Advantages;
