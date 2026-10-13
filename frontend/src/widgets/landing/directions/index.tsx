import { CommissionOfferBlock } from "@/features/commission-application";
import BlockHeading from "@/shared/ui/block-heading";
import { DIRECTIONS_DATA } from "./data";
import styles from "./style.module.scss";

const Directions = () => {
  return (
    <section id="directions" className={styles.block}>
      <div className={styles.content}>
        <BlockHeading size="large" title={DIRECTIONS_DATA.title} subtitle={DIRECTIONS_DATA.description} />
      </div>

      <div className={styles.offer}>
        <CommissionOfferBlock />
      </div>
    </section>
  );
};

export default Directions;
