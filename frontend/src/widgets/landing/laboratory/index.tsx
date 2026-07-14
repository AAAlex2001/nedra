import AccentLine from "@/shared/ui/accent-line";
import { LABORATORY_DATA, NUMBERED_CARDS, WIDE_CARDS } from "./data";
import NumberedCards from "./ui/numbered-card";
import WideCards from "./ui/wide-card";
import styles from "./style.module.scss";

const Laboratory = () => {
  return (
    <section id="laboratory" className={styles.section}>
      <header className={styles.header}>
        <h2 className={styles.title}>
          {LABORATORY_DATA.titleBefore}{" "}
          <span className={styles.titleAccent}>{LABORATORY_DATA.titleAccent}</span>{" "}
          {LABORATORY_DATA.titleAfter}
        </h2>
        <AccentLine width={30} />
        <p className={styles.subtitle}>{LABORATORY_DATA.subtitle}</p>
      </header>

      <div className={styles.grid}>
        <NumberedCards cards={NUMBERED_CARDS} />

        <div className={styles.rowWide}>
          <WideCards cards={WIDE_CARDS} />
        </div>
      </div>
    </section>
  );
};

export default Laboratory;
