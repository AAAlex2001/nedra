import type { FieldSection } from "../../data";
import styles from "./style.module.scss";

type FieldsDetailsProps = {
  sections: FieldSection[];
};

const FieldsDetails = ({ sections }: FieldsDetailsProps) => {
  if (sections.length === 0) {
    return null;
  }

  return (
    <div className={styles.body}>
      {sections.map((section) => (
        <div key={section.title} className={styles.section}>
          <h4 className={styles.title}>{section.title}</h4>
          {section.bullets ? (
            <ul className={styles.list}>
              {section.bullets.map((bullet) => (
                <li key={bullet} className={styles.item}>
                  <span className={styles.dot} aria-hidden="true" />
                  <span>{bullet}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className={styles.text}>{section.text}</p>
          )}
        </div>
      ))}
    </div>
  );
};

export default FieldsDetails;
