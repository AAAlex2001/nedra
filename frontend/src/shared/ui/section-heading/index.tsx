import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type SectionHeadingProps = {
  title: string;
};

const SectionHeading = ({ title }: SectionHeadingProps) => (
  <div className={styles.heading}>
    <h1 className={styles.title}>{title}</h1>
    <AccentLine width={50} />
  </div>
);

export default SectionHeading;
