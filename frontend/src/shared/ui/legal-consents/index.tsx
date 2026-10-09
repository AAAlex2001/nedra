import Link from "next/link";
import { LEGAL_PAGES } from "@/shared/config/legal";
import Checkbox from "@/shared/ui/checkbox";
import styles from "./style.module.scss";

const CONSENTS = [
  { lead: "Я соглашаюсь с", text: "Политикой конфиденциальности", href: LEGAL_PAGES.privacy.href },
  { lead: "Я соглашаюсь с", text: "Пользовательским соглашением", href: LEGAL_PAGES.agreement.href },
  { lead: "Я даю", text: "Согласие на обработку персональных данных", href: LEGAL_PAGES.consent.href },
];

const LegalConsents = () => (
  <div className={styles.consents}>
    {CONSENTS.map((consent) => (
      <Checkbox key={consent.href} required>
        {consent.lead}{" "}
        <Link href={consent.href} className={styles.link} target="_blank">
          {consent.text}
        </Link>
      </Checkbox>
    ))}
  </div>
);

export default LegalConsents;
