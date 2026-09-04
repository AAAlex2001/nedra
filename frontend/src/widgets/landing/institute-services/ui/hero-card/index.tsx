import Image from "next/image";
import type { Direction } from "@/entities/service";
import styles from "./style.module.scss";

type HeroCardProps = {
  direction: Direction;
};

const HeroCard = ({ direction }: HeroCardProps) => (
  <div className={styles.card}>
    <Image
      className={styles.image}
      src={direction.image}
      alt=""
      fill
      sizes="(min-width: 1440px) 816px, (min-width: 768px) calc(100vw - 140px), calc(100vw - 40px)"
      quality={82}
      decoding="async"
      loading="lazy"
      aria-hidden="true"
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
