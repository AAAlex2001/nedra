import Image from "next/image";
import AccentLine from "@/shared/ui/accent-line";
import OutlineButton from "@/shared/ui/outline-button";
import { HERO_DATA } from "./data";
import styles from "./style.module.scss";

const CHIP_CLASSES = [styles.chip0, styles.chip1, styles.chip2, styles.chip3];

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

        <OutlineButton href={HERO_DATA.button.href}>
          {HERO_DATA.button.text}
        </OutlineButton>
      </div>

      <div className={styles.stage}>
        <div className={styles.pic} aria-hidden="true">
          <Image
            className={styles.picImage}
            src="/globe/globe.webp"
            alt=""
            fill
            sizes="(min-width: 768px) 597px, (min-width: 360px) 360px, 100vw"
            quality={82}
            decoding="async"
            preload
          />
        </div>
        {HERO_DATA.advantages.slice(0, 4).map((item, index) => (
          <div key={item.title} className={`${styles.accordion} ${CHIP_CLASSES[index]}`}>
            <span className={styles.accordionText}>{item.title}</span>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Hero;
