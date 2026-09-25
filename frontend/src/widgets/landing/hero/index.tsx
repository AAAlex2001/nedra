import AccentLine from "@/shared/ui/accent-line";
import Button from "@/shared/ui/button";
import OutlineButton from "@/shared/ui/outline-button";
import { HERO_DATA } from "./data";
import BlitzWindow from "./ui/blitz-window";
import styles from "./style.module.scss";

const Hero = () => {
  return (
    <section className={styles.hero}>
      <div className={styles.headings}>
        <div className={styles.headingsInner}>
          <p className={styles.kicker}>{HERO_DATA.kicker}</p>
          <AccentLine width={50} />
          <h1 className={styles.title}>
            {HERO_DATA.titleBefore}{" "}
            <span className={styles.titleBold}>{HERO_DATA.titleHighlight}</span>
          </h1>
        </div>

        <div className={styles.actions}>
          <OutlineButton href={HERO_DATA.button.href}>
            {HERO_DATA.button.text}
          </OutlineButton>
          <Button href="#request" className={styles.sunButton}>
            Оставить заявку
          </Button>
        </div>
      </div>

      <div className={styles.stage}>
        <BlitzWindow />
      </div>
    </section>
  );
};

export default Hero;
