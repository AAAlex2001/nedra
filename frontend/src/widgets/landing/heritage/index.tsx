import CompareSlider from "./ui/compare-slider";
import HeritageHeading from "./ui/heading";
import InfoPanels from "./ui/info-panel";
import ServiceCards from "./ui/service-card";
import styles from "./style.module.scss";

const Heritage = () => {
  return (
    <section className={styles.section}>
      <div className={styles.top}>
        <CompareSlider />

        <div className={styles.right}>
          <HeritageHeading />
          <ServiceCards />
        </div>
      </div>

      <InfoPanels />
    </section>
  );
};

export default Heritage;
