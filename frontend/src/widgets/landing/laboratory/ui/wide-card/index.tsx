import type { WideCardItem } from "../../data";
import styles from "./style.module.scss";

type WideCardsProps = {
  cards: WideCardItem[];
};

const WideCards = ({ cards }: WideCardsProps) => {
  return (
    <>
      {cards.map((item) => (
        <article key={item.title} className={styles.card}>
          <div className={styles.titleRow}>
            <h3 className={styles.title}>{item.title}</h3>
          </div>
          <ul className={styles.list}>
            {item.items.map((listItem) => (
              <li key={listItem}>{listItem}</li>
            ))}
          </ul>
        </article>
      ))}
    </>
  );
};

export default WideCards;
