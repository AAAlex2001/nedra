import AccentLine from "@/shared/ui/accent-line";
import { ACTIVITIES_DATA } from "../../data";
import FeatureList from "../feature-list";
import MethodologyCard from "../methodology-card";
import styles from "./style.module.scss";

const ActivitiesContent = () => {
  return (
    <div className={styles.layout}>
      <div className={styles.left}>
        <div className={styles.heading}>
          <h2 className={styles.title}>
            {ACTIVITIES_DATA.titleBefore}{" "}
            <span className={styles.titleAccent}>
              {ACTIVITIES_DATA.titleAccent}
            </span>
          </h2>
          <AccentLine width={30} />
          <p className={styles.subtitle}>{ACTIVITIES_DATA.subtitle}</p>
        </div>

        <FeatureList />
      </div>

      <MethodologyCard />
    </div>
  );
};

export default ActivitiesContent;
