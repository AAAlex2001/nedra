import AccentLine from "@/shared/ui/accent-line";
import { SERVICES_DATA } from "./data";
import ServiceCards from "./ui/service-card";
import styles from "./style.module.scss";

const Services = () => {
  return (
    <section className={styles.section}>
      <div className={styles.heading}>
        <h2 className={styles.title}>{SERVICES_DATA.title}</h2>
        <AccentLine width={150} />
      </div>

      <div className={styles.grid}>
        <ServiceCards />
      </div>
    </section>
  );
};

export default Services;
