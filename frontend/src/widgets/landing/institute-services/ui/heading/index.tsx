import AccentLine from "@/shared/ui/accent-line";
import { SERVICES_DATA } from "../../data";
import styles from "./style.module.scss";

const Heading = () => (
  <div className={styles.heading}>
    <h2 className={styles.title}>{SERVICES_DATA.title}</h2>
    <AccentLine width={30} />
    <p className={styles.subtitle}>{SERVICES_DATA.subtitle}</p>
  </div>
);

export default Heading;
