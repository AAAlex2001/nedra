import AccentLine from "@/shared/ui/accent-line";
import OutlineButton from "@/shared/ui/outline-button";
import { HERO_ACCORDION_LAYOUT, HERO_DATA } from "./data";
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

        <OutlineButton href={HERO_DATA.button.href}>
          {HERO_DATA.button.text}
        </OutlineButton>
      </div>

      <div className={styles.pic} />

      {HERO_DATA.advantages.slice(0, 4).map((item, i) => {
        const layout = HERO_ACCORDION_LAYOUT[i];
        if (!layout) return null;
        return (
          <div
            key={item.title}
            className={styles.accordion}
            style={{
              left: layout.left,
              top: layout.top,
              width: layout.width,
              height: layout.height,
              zIndex: layout.zIndex,
            }}
          >
            <span className={styles.accordionText}>{item.title}</span>
          </div>
        );
      })}
    </section>
  );
};

export default Hero;
