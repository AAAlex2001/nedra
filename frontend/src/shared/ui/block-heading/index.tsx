import AccentLine from "@/shared/ui/accent-line";
import styles from "./style.module.scss";

type BlockHeadingProps = {
  title: string;
  subtitle: string;
  size?: "default" | "large";
  titleId?: string;
};

const BlockHeading = ({ title, subtitle, size = "default", titleId }: BlockHeadingProps) => (
  <div className={styles.heading}>
    <h2 id={titleId} className={`${styles.title} ${size === "large" ? styles.large : ""}`}>{title}</h2>
    <AccentLine width={30} />
    <p className={styles.subtitle}>{subtitle}</p>
  </div>
);

export default BlockHeading;
