"use client";

import Image from "next/image";
import { useCommissionPopup } from "@/features/commission-application";
import styles from "./style.module.scss";

const POINTS = [
  "Проекты консервации и ликвидации",
  "Проекты технического перевооружения",
  "Декларации промышленной безопасности",
  "Обоснования безопасности",
];

const DECOR = ["/services/2.webp", "/services/3.webp", "/services/4.webp", "/services/7.webp"];

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

const CommissionPromo = () => {
  const { openForm } = useCommissionPopup();

  return (
    <aside className={styles.promo}>
      <div className={styles.card}>
        <div className={styles.media}>
          <Image
            className={styles.image}
            src="/services/1.webp"
            alt="Проектная документация, геодезический прибор и лабораторная колба"
            width={1600}
            height={700}
            sizes="(min-width: 1440px) 900px, 100vw"
          />
        </div>

        <div className={styles.content}>
          <span className={styles.badge}>Конкурсный отбор</span>

          <p className={styles.title}>Примем эксперта</p>
          <p className={styles.lead}>
            для выполнения работ по экспертизе промышленной безопасности следующих объектов:
          </p>

          <ul className={styles.points}>
            {POINTS.map((text) => (
              <li key={text} className={styles.point}>
                <Check />
                <span className={styles.pointText}>{text}</span>
              </li>
            ))}
          </ul>

          <button type="button" className={styles.primary} onClick={openForm}>
            Оставить заявку в конкурсную комиссию
          </button>

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
};

export default CommissionPromo;
