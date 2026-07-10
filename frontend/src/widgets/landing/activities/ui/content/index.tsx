import AccentLine from "@/shared/ui/accent-line";
import type { FeatureItem, MethodologyCardData } from "../../data";
import FeatureList from "../feature-list";
import MethodologyCard from "../methodology-card";
import styles from "./style.module.scss";

type ActivitiesContentProps = {
  heading: {
    titleBefore: string;
    titleAccent: string;
    subtitle: string;
  };
  features: FeatureItem[];
  card: MethodologyCardData;
};

const ActivitiesContent = ({ heading, features, card }: ActivitiesContentProps) => {
  return (
    <div className={styles.layout}>
      <div className={styles.left}>
        <div className={styles.heading}>
          <h2 className={styles.title}>
            {heading.titleBefore}{" "}
            <span className={styles.titleAccent}>{heading.titleAccent}</span>
          </h2>
          <AccentLine width={30} />
          <p className={styles.subtitle}>{heading.subtitle}</p>
        </div>

        <FeatureList items={features} />
      </div>

      <MethodologyCard card={card} />
    </div>
  );
};

export default ActivitiesContent;
