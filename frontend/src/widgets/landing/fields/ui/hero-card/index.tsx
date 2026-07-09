import type { FieldItem } from "../../data";
import styles from "./style.module.scss";

type FieldsHeroCardProps = {
  item: FieldItem;
};

const FieldsHeroCard = ({ item }: FieldsHeroCardProps) => {
  return (
    <div className={styles.card}>
      <div
        className={styles.image}
        style={{ backgroundImage: `url(${item.image})` }}
        aria-hidden
      />
      <div className={styles.fade} aria-hidden />
      <div className={styles.content}>
        <span className={styles.number}>{item.id}</span>
        <h3 className={styles.title}>{item.title}</h3>
        <p className={styles.summary}>{item.summary}</p>
      </div>
    </div>
  );
};

export default FieldsHeroCard;
