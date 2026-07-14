import { OBSUZHDENIYA } from "./data";
import styles from "./style.module.scss";

const ObshchestvennyeObsuzhdeniya = () => (
  <div className={styles.list}>
    {OBSUZHDENIYA.map((item) => (
      <a
        key={item.href}
        className={styles.card}
        href={item.href}
        target="_blank"
        rel="noopener noreferrer"
      >
        <span className={styles.label}>{item.label}</span>
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

export default ObshchestvennyeObsuzhdeniya;
