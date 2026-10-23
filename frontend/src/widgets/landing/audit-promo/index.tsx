import Image from "next/image";
import Link from "next/link";
import styles from "./style.module.scss";

const FEATURES = [
  {
    title: "Без выезда на объект",
    text: "Загрузите документы онлайн — их проверят штатные аудиторы института.",
  },
  {
    title: "Понятные рекомендации",
    text: "По каждому несоответствию — что нужно исправить и какие документы подготовить.",
  },
  {
    title: "Отчёт с ЭЦП",
    text: "Получите результат аудита в электронном виде.",
  },
];

const AuditPromo = () => (
  <section className={styles.section} aria-labelledby="audit-promo-title">
    <div className={styles.card}>
      <div className={styles.content}>
        <span className={styles.badge}>Блиц-аудит</span>
        <h2 className={styles.title} id="audit-promo-title">
          Аудит промышленной безопасности онлайн
        </h2>
        <p className={styles.lead}>
          Проверьте систему управления промышленной безопасностью по документам. От загрузки файлов
          до отчёта с ЭЦП — всё в личном кабинете.
        </p>

        <div className={styles.actions}>
          <Link className={styles.primary} href="/blits-audit">
            Начать аудит
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="M5 12h14m-6-6 6 6-6 6"
                stroke="currentColor"
                strokeWidth="1.7"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </Link>
          <Link className={styles.secondary} href="/blits-audit#perechen">
            Какие документы нужны
          </Link>
        </div>
      </div>

      <div className={styles.media}>
        <Image
          className={styles.image}
          src="/audit/13.webp"
          alt="Чек-лист аудита, техническая документация и промышленное оборудование"
          width={1600}
          height={700}
          sizes="(min-width: 1440px) 580px, (min-width: 1100px) 45vw, (min-width: 768px) 668px, 100vw"
        />
        <span className={styles.mediaCaption}>Документы → Проверка → Отчёт с ЭЦП</span>
      </div>

      <ul className={styles.features}>
        {FEATURES.map((feature) => (
          <li className={styles.feature} key={feature.title}>
            <svg
              className={styles.check}
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="m6 12 4 4 8-8"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div>
              <h3 className={styles.featureTitle}>{feature.title}</h3>
              <p className={styles.featureText}>{feature.text}</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  </section>
);

export default AuditPromo;
