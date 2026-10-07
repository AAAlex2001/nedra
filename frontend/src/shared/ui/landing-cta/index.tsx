import Image from "next/image";
import type { ReactNode } from "react";
import { CheckIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type LandingCtaProps = {
  badge: string;
  title: string;
  points: string[];
  image: string;
  imageAlt: string;
  decor: string[];
  action: ReactNode;
};

const LandingCta = ({ badge, title, points, image, imageAlt, decor, action }: LandingCtaProps) => (
  <section className={styles.cta}>
    <div className={styles.card}>
      <div className={styles.media}>
        <Image
          className={styles.image}
          src={image}
          alt={imageAlt}
          width={1600}
          height={700}
          sizes="(min-width: 1440px) 1168px, 100vw"
        />
      </div>

      <div className={styles.content}>
        <span className={styles.badge}>{badge}</span>

        <h2 className={styles.title}>{title}</h2>

        <ul className={styles.points}>
          {points.map((text) => (
            <li key={text} className={styles.point}>
              <CheckIcon className={styles.pointIcon} />
              <span className={styles.pointText}>{text}</span>
            </li>
          ))}
        </ul>

        <div className={styles.buttons}>{action}</div>

        <div className={styles.decor} aria-hidden="true">
          {decor.map((src) => (
            <Image key={src} className={styles.decorImage} src={src} alt="" width={180} height={180} />
          ))}
        </div>
      </div>
    </div>
  </section>
);

export default LandingCta;
