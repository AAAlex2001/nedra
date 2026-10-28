import { pluralize } from "@/shared/lib/text";
import SectionHeading from "@/shared/ui/section-heading";
import styles from "./style.module.scss";

type ArticlesHeadingProps = {
  title: string;
  subtitle: string;
  total: number;
};

const COUNT_FORMS: [string, string, string] = ["материал", "материала", "материалов"];

const ArticlesHeading = ({ title, subtitle, total }: ArticlesHeadingProps) => {
  const countText = `${total} ${pluralize(total, COUNT_FORMS)}`;

  return (
    <div className={styles.heading}>
      <SectionHeading title={title} />

      <div className={styles.row}>
        <p className={styles.subtitle}>{subtitle}</p>
        <span className={styles.count}>{countText}</span>
      </div>
    </div>
  );
};

export default ArticlesHeading;
