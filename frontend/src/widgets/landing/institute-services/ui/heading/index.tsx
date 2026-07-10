import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type HeadingProps = {
  title: string;
  subtitle: string;
};

const Heading = ({ title, subtitle }: HeadingProps) => (
  <div className={styles.heading}>
    <h2 className={styles.title}>{title}</h2>
    <AccentLine width={30} />
    <p className={styles.subtitle}>{subtitle}</p>
  </div>
);

export default Heading;
