import Image from "next/image";
import Button from "@/shared/ui/button";
import styles from "./style.module.scss";

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

const DECOR = ["/blitz/24.png", "/blitz/25.png", "/blitz/26.png", "/blitz/27.png"];

const POINTS = [
  "Заявку сразу видят эксперты с нужной аттестацией",
  "Цена из тарифа института известна до регистрации",
  "Заключение с ЭЦП, счёт и акт — в личном кабинете",
];

const BlitsPromo = () => (
  <aside className={styles.promo}>
    <div className={styles.card}>
      <div className={styles.media}>
        <Image
          className={styles.image}
          src="/blitz/23.png"
          alt="Документация, заключение с электронной подписью и технические устройства опасного производственного объекта"
          width={1600}
          height={700}
          sizes="(min-width: 1440px) 1168px, 100vw"
        />
      </div>

      <div className={styles.content}>
        <span className={styles.badge}>Блиц-эксперт</span>

        <p className={styles.title}>Экспертиза промышленной безопасности от 1 дня</p>

        <ul className={styles.points}>
          {POINTS.map((text) => (
            <li key={text} className={styles.point}>
              <Check />
              <span className={styles.pointText}>{text}</span>
            </li>
          ))}
        </ul>

        <div className={styles.buttons}>
          <Button className={styles.button} href="/blits-ekspert">
            Узнать стоимость
          </Button>
          <a className={styles.secondary} href="/blits-ekspert#kak-prohodit">
            Как это работает
          </a>
        </div>

        <div className={styles.decor} aria-hidden="true">
          {DECOR.map((src) => (
            <Image
              key={src}
              className={styles.decorImage}
              src={src}
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

export default BlitsPromo;
