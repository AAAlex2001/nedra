import Card from "@/shared/ui/card";
import { UserCircleIcon } from "@/shared/ui/icons";
import SectionHeading from "@/shared/ui/section-heading";
import { RUKOVODSTVO } from "./data";
import styles from "./style.module.scss";

const SvedeniyaRukovodstvo = () => {
  const { title, notice, subtitle, fields, footer } = RUKOVODSTVO;

  return (
    <>
      <SectionHeading title={title} />

      <Card gap={20}>
        <div className={styles.note}>
          <UserCircleIcon className={styles.noteIcon} />
          <p className={styles.noteText}>{notice}</p>
        </div>

        <div className={styles.leader}>
          <h2 className={styles.subtitle}>{subtitle}</h2>
          <div className={styles.table}>
            {fields.map((field) => (
              <div key={field.label} className={styles.field}>
                <span className={styles.fieldLabel}>{field.label}</span>
                <span className={styles.fieldValue}>{field.value}</span>
              </div>
            ))}
          </div>
        </div>

        <p className={styles.footer}>{footer}</p>
      </Card>
    </>
  );
};

export default SvedeniyaRukovodstvo;
