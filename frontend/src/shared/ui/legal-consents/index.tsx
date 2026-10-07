import Link from "next/link";
import { LEGAL_PAGES } from "@/shared/config/legal";
import styles from "./style.module.scss";

const CONSENTS = [
  { lead: "Я соглашаюсь с", text: "Политикой конфиденциальности", href: LEGAL_PAGES.privacy.href },
  { lead: "Я соглашаюсь с", text: "Пользовательским соглашением", href: LEGAL_PAGES.agreement.href },
  { lead: "Я даю", text: "Согласие на обработку персональных данных", href: LEGAL_PAGES.consent.href },
];

const LegalConsents = () => (
  <div className={styles.consents}>
    {CONSENTS.map((consent) => (
      <label key={consent.href} className={styles.checkbox}>
        <input type="checkbox" className={styles.input} required />
        <span className={styles.box} aria-hidden="true">
          <svg className={styles.mark} viewBox="0 0 16 16" fill="none">
            <path
              d="M3.5 8.5L6.5 11.5L12.5 5"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
        <span className={styles.label}>
          {consent.lead}{" "}
          <Link href={consent.href} className={styles.link} target="_blank">
            {consent.text}
          </Link>
        </span>
      </label>
    ))}
  </div>
);

export default LegalConsents;
