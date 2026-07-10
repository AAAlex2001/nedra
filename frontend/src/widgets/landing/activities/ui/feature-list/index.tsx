import {
  CertifiedMethodIcon,
  OfficialCertificateIcon,
  OfficialResultsIcon,
} from "@/shared/ui/icons";
import type { FeatureItem } from "../../data";
import styles from "./style.module.scss";

const ICONS = {
  certified: CertifiedMethodIcon,
  certificate: OfficialCertificateIcon,
  results: OfficialResultsIcon,
} as const;

type FeatureListProps = {
  items: FeatureItem[];
};

const FeatureList = ({ items }: FeatureListProps) => {
  return (
    <div className={styles.list}>
      {items.map((item) => {
        const Icon = ICONS[item.icon];

        return (
          <div key={item.title} className={styles.item}>
            <Icon className={styles.icon} />
            <div className={styles.text}>
              <h3 className={styles.title}>{item.title}</h3>
              <p className={styles.description}>{item.description}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default FeatureList;
