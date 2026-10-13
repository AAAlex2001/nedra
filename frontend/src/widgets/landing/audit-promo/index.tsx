import Link from "next/link";
import BlockHeading from "@/shared/ui/block-heading";
import BlitzWindow from "../hero/ui/blitz-window";
import styles from "./style.module.scss";

const AuditPromo = () => (
  <section className={styles.section} aria-labelledby="audit-promo-title">
    <div className={styles.window}><BlitzWindow variant="audit" /></div>
    <div className={styles.intro}>
      <BlockHeading
        size="large"
        titleId="audit-promo-title"
        title="Обеспечим проведение аудита систем управления промышленной безопасностью"
        subtitle={'Пункт 6 статьи 11 Федерального закона от 21.07.1997 № 116-ФЗ «О промышленной безопасности опасных производственных объектов»'}
      />
      <Link className={styles.link} href="/blits-audit#perechen">
        Какие документы нужны
      </Link>
    </div>
  </section>
);

export default AuditPromo;
