import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type HeritageHeadingProps = {
  titleBefore: string;
  titleAccent: string;
};

const HeritageHeading = ({ titleBefore, titleAccent }: HeritageHeadingProps) => (
  <div className={styles.heading}>
    <h2 className={styles.title}>
      {titleBefore}
      <br />
      <span className={styles.titleAccent}>{titleAccent}</span>
    </h2>
    <AccentLine width={30} />
  </div>
);

export default HeritageHeading;
