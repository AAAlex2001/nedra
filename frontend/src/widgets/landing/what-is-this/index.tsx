import AccentLine from "@/shared/ui/accent-line";
import { WHAT_IS_THIS_CARDS, WHAT_IS_THIS_DATA } from "./data";
import ServiceCards from "./ui/service-card";
import styles from "./style.module.scss";

const WhatIsThis = () => {
  return (
    <section id="about" className={styles.section}>
      <div className={styles.heading}>
        <h2 className={styles.title}>{WHAT_IS_THIS_DATA.title}</h2>
        <AccentLine width={150} />
      </div>

      <div className={styles.grid}>
        <ServiceCards cards={WHAT_IS_THIS_CARDS} />
      </div>
    </section>
  );
};

export default WhatIsThis;
