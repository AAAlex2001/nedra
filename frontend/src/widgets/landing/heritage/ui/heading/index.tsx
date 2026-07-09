import AccentLine from "@/shared/ui/accent-line";
import { HERITAGE_DATA } from "../../data";
import styles from "./style.module.scss";

const HeritageHeading = () => {
  return (
    <div className={styles.heading}>
      <h2 className={styles.title}>
        {HERITAGE_DATA.titleBefore}
        <br />
        <span className={styles.titleAccent}>{HERITAGE_DATA.titleAccent}</span>
      </h2>
      <AccentLine width={30} />
    </div>
  );
};

export default HeritageHeading;
