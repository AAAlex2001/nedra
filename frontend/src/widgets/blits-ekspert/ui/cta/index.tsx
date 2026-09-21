import Image from "next/image";
import { CheckIcon } from "@/shared/ui/icons";
import StartButtons from "../start-buttons";
import styles from "./style.module.scss";

const POINTS = [
  "Заявку сразу видят эксперты с нужной аттестацией",
  "Цена из тарифа института известна до регистрации",
  "Заключение с ЭЦП, счёт и акт — в личном кабинете",
];

const DECOR = ["/blitz/19.png", "/blitz/20.png", "/blitz/21.png", "/blitz/22.png"];

const Cta = () => (
  <section className={styles.cta}>
    <div className={styles.card}>
      <div className={styles.media}>
        <Image
          className={styles.image}
          src="/blitz/18.png"
          alt="Документация, заключение с электронной подписью и технические устройства опасного производственного объекта"
          width={1600}
          height={700}
          sizes="(min-width: 1440px) 1168px, 100vw"
        />
      </div>

      <div className={styles.content}>
        <span className={styles.badge}>Экспертиза от 1 дня</span>

        <h2 className={styles.title}>Отправьте документацию на экспертизу</h2>

        <ul className={styles.points}>
          {POINTS.map((text) => (
            <li key={text} className={styles.point}>
              <CheckIcon className={styles.pointIcon} />
              <span className={styles.pointText}>{text}</span>
            </li>
          ))}
        </ul>

        <div className={styles.buttons}>
          <StartButtons secondaryHref="#kak-prohodit" secondaryText="Как это работает" />
        </div>

        <div className={styles.decor} aria-hidden="true">
          {DECOR.map((src) => (
            <Image key={src} className={styles.decorImage} src={src} alt="" width={180} height={180} />
          ))}
        </div>
      </div>
    </div>
  </section>
);

export default Cta;
