import { NUMBERED_CARDS } from "./data";
import styles from "./style.module.scss";

const NumberedCards = () => {
  return (
    <>
      <div className={styles.row}>
        {NUMBERED_CARDS.slice(0, 3).map((item) => (
          <article key={item.number} className={styles.card}>
            <p className={styles.text}>{item.text}</p>
            <div className={styles.numberCol}>
              <span className={styles.number}>{item.number}</span>
            </div>
          </article>
        ))}
      </div>

      <div className={`${styles.row} ${styles.rowTall}`}>
        {NUMBERED_CARDS.slice(3, 6).map((item) => (
          <article key={item.number} className={styles.card}>
            <p className={styles.text}>{item.text}</p>
            <div className={styles.numberCol}>
              <span className={styles.number}>{item.number}</span>
            </div>
          </article>
        ))}
      </div>
    </>
  );
};

export default NumberedCards;
