import type { NumberedCardItem } from "../../data";
import styles from "./style.module.scss";

type NumberedCardsProps = {
  cards: NumberedCardItem[];
};

const NumberedCards = ({ cards }: NumberedCardsProps) => {
  return (
    <>
      <div className={styles.row}>
        {cards.slice(0, 3).map((item) => (
          <article key={item.number} className={styles.card}>
            <p className={styles.text}>{item.text}</p>
            <div className={styles.numberCol}>
              <span className={styles.number}>{item.number}</span>
            </div>
          </article>
        ))}
      </div>

      <div className={`${styles.row} ${styles.rowTall}`}>
        {cards.slice(3, 6).map((item) => (
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
