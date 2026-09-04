import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type BlockHeadingProps = {
  title: string;
  subtitle: string;
};

const BlockHeading = ({ title, subtitle }: BlockHeadingProps) => (
  <div className={styles.heading}>
    <h2 className={styles.title}>{title}</h2>
    <AccentLine width={30} />
    <p className={styles.subtitle}>{subtitle}</p>
  </div>
);

export default BlockHeading;
