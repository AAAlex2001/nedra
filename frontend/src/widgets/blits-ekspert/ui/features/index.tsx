import { FEATURES } from "../../data";
import IconTile from "../icon-tile";
import styles from "./style.module.scss";

const Features = () => (
  <section className={styles.features}>
    <h2 className={styles.title}>Экспертиза без переписки и ожидания</h2>

    <div className={styles.grid}>
      {FEATURES.map((card) => (
        <article key={card.title} className={styles.card}>
          <IconTile icon={card.icon} />
          <h3 className={styles.cardTitle}>{card.title}</h3>
          <p className={styles.cardText}>{card.text}</p>
        </article>
      ))}
    </div>
  </section>
);

export default Features;
