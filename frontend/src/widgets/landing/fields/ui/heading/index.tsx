import AccentLine from "@/shared/ui/accent-line";
import { FIELDS_DATA } from "../../data";
import styles from "./style.module.scss";

const FieldsHeading = () => {
  return (
    <div className={styles.heading}>
      <h2 className={styles.title}>{FIELDS_DATA.title}</h2>
      <AccentLine width={30} />
      <p className={styles.subtitle}>{FIELDS_DATA.subtitle}</p>
    </div>
  );
};

export default FieldsHeading;
