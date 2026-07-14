import { SVEDENIYA_BASE, SVEDENIYA_SECTIONS } from "@/shared/ui/svedeniya-nav/data";
import styles from "./style.module.scss";

const SvedeniyaCards = () => (
  <div className={styles.cards}>
    {SVEDENIYA_SECTIONS.map((section, index) => (
      <a
        key={section.slug}
        className={styles.card}
        href={`${SVEDENIYA_BASE}/${section.slug}`}
      >
        <span className={styles.number}>
          {String(index + 1).padStart(2, "0")}
        </span>
        <span className={styles.label}>{section.label}</span>
        <svg
          className={styles.chevron}
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path
            d="M9 6L15 12L9 18"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </a>
    ))}
  </div>
);

export default SvedeniyaCards;
