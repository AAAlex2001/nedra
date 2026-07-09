import { WIDE_CARDS } from "./data";
import styles from "./style.module.scss";

const WideCards = () => {
  return (
    <>
      {WIDE_CARDS.map((item) => (
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
