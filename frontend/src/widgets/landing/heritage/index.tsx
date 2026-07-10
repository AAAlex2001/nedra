import { COMPARE_SLIDER, HERITAGE_DATA, INFO_PANELS, SERVICE_CARDS } from "./data";
import CompareSlider from "./ui/compare-slider";
import HeritageHeading from "./ui/heading";
import InfoPanels from "./ui/info-panel";
import ServiceCards from "./ui/service-card";
import styles from "./style.module.scss";

const Heritage = () => {
  return (
    <section className={styles.section}>
      <div className={styles.top}>
        <CompareSlider data={COMPARE_SLIDER} />

        <div className={styles.right}>
          <HeritageHeading
            titleBefore={HERITAGE_DATA.titleBefore}
            titleAccent={HERITAGE_DATA.titleAccent}
          />
          <ServiceCards cards={SERVICE_CARDS} />
        </div>
      </div>

      <InfoPanels panels={INFO_PANELS} />
    </section>
  );
};

export default Heritage;
