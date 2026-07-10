import type { Direction } from "../../data";
import styles from "./style.module.scss";

type HeroCardProps = {
  direction: Direction;
};

const HeroCard = ({ direction }: HeroCardProps) => (
  <div className={styles.card}>
    <div
      className={styles.image}
      style={{ backgroundImage: `url(${direction.image})` }}
      aria-hidden
    />
    <div className={styles.fade} aria-hidden />
    <div className={styles.content}>
      <span className={styles.number}>{direction.id}</span>
      <h3 className={styles.title}>{direction.heroTitle}</h3>
      <p className={styles.summary}>{direction.summary}</p>
    </div>
  </div>
);

export default HeroCard;
