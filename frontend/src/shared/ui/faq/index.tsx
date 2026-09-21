import styles from "./style.module.scss";

export type FaqItem = {
  question: string;
  answer: string;
};

type FaqProps = {
  items: FaqItem[];
  title?: string;
};

const Chevron = () => (
  <svg
    className={styles.chevron}
    width="20"
    height="20"
    viewBox="0 0 20 20"
    fill="none"
    aria-hidden="true"
  >
    <path
      d="M5 7.5L10 12.5L15 7.5"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const Faq = ({ items, title }: FaqProps) => (
  <section className={styles.faq}>
    {title && <h2 className={styles.title}>{title}</h2>}

    <div className={styles.card}>
      {items.map((item) => (
        <details key={item.question} className={styles.item}>
          <summary className={styles.question}>
            <span className={styles.questionText}>{item.question}</span>
            <Chevron />
          </summary>
          <p className={styles.answer}>{item.answer}</p>
        </details>
      ))}
    </div>
  </section>
);

export default Faq;
