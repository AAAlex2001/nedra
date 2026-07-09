import type { FieldItem } from "../../data";
import FieldsContact from "../contact";
import FieldsDetails from "../details";
import FieldsHeroCard from "../hero-card";
import FieldsLicenses from "../licenses";
import styles from "./style.module.scss";

type FieldsDrawerProps = {
  item: FieldItem;
};

const FieldsDrawer = ({ item }: FieldsDrawerProps) => {
  return (
    <aside className={styles.drawer} role="tabpanel">
      <FieldsHeroCard item={item} />

      <div className={styles.stack}>
        <FieldsContact />
        <FieldsDetails sections={item.sections} />
      </div>

      <FieldsLicenses item={item} />
    </aside>
  );
};

export default FieldsDrawer;
