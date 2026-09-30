import { CommissionOfferBlock } from "@/features/commission-application";
import AccentLine from "@/shared/ui/accent-line";
import { DIRECTIONS_DATA } from "./data";
import styles from "./style.module.scss";

const Directions = () => {
  return (
    <section id="directions" className={styles.block}>
      <div className={styles.content}>
        <div className={styles.heading}>
          <h2 className={styles.title}>{DIRECTIONS_DATA.title}</h2>
          <AccentLine width={30} />
          <p className={styles.description}>{DIRECTIONS_DATA.description}</p>
        </div>
      </div>

      <div className={styles.offer}>
        <CommissionOfferBlock />
      </div>
    </section>
  );
};

export default Directions;
