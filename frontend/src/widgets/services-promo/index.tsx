import Image from "next/image";
import { DIRECTIONS } from "@/entities/service";
import styles from "./style.module.scss";

const POINTS = [
  "Проектирование, инженерные изыскания и научно-техническое сопровождение",
  "Промышленная безопасность, экология и объекты культурного наследия",
  "Собственная лаборатория, сертификация, обучение и атомная лицензия",
];

const Check = () => (
  <svg className={styles.pointIcon} viewBox="0 0 20 20" fill="none" aria-hidden="true">
    <circle cx="10" cy="10" r="9" stroke="currentColor" strokeWidth="1.6" />
    <path
      d="M6 10.2L8.8 13L14 7.8"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const ServicesPromo = () => (
  <aside className={styles.promo}>
    <div className={styles.card}>
      <div className={styles.media}>
        <Image
          className={styles.image}
          src="/services/1.webp"
          alt="Проектирование, инженерные изыскания и лабораторные испытания НПИ «Недра»"
          width={1600}
          height={700}
          sizes="(min-width: 1440px) 900px, 100vw"
        />
      </div>

      <div className={styles.content}>
        <span className={styles.badge}>НПИ «Недра»</span>

        <p className={styles.title}>Девять направлений института</p>

        <ul className={styles.points}>
          {POINTS.map((text) => (
            <li key={text} className={styles.point}>
              <Check />
              <span className={styles.pointText}>{text}</span>
            </li>
          ))}
        </ul>

        <div className={styles.buttons}>
          <a className={styles.primary} href="#services">
            Посмотреть все услуги
          </a>
          <a className={styles.secondary} href="#request">
            Оставить заявку
          </a>
        </div>

        <div className={styles.decor} aria-hidden="true">
          {DIRECTIONS.map((direction, index) => (
            <Image
              key={direction.id}
              className={styles.decorImage}
              src={`/services/${index + 2}.webp`}
              alt=""
              width={180}
              height={180}
            />
          ))}
        </div>
      </div>
    </div>
  </aside>
);

export default ServicesPromo;
