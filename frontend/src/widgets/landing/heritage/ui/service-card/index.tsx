import {
  HeritageDesignIcon,
  HeritageRepairIcon,
} from "@/shared/ui/icons";
import { SERVICE_CARDS } from "./data";
import styles from "./style.module.scss";

const ICONS = {
  design: HeritageDesignIcon,
  repair: HeritageRepairIcon,
} as const;

const ServiceCards = () => {
  return (
    <div className={styles.list}>
      {SERVICE_CARDS.map((item) => {
        const Icon = ICONS[item.icon];

        return (
          <article key={item.number} className={styles.card}>
            <Icon className={styles.icon} />
            <span
              className={styles.number}
              style={{ left: `${item.badgeLeft}px` }}
            >
              {item.number}
            </span>
            <div className={styles.text}>
              <h3 className={styles.title}>{item.title}</h3>
              <p className={styles.description}>{item.description}</p>
            </div>
          </article>
        );
      })}
    </div>
  );
};

export default ServiceCards;
