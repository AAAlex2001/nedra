import DocsCard from "@/shared/ui/docs-card";
import { PeopleIcon } from "@/shared/ui/icons";
import InfoCard from "@/shared/ui/info-card";
import SectionHeading from "@/shared/ui/section-heading";
import { SVEDENIYA_STRUKTURA } from "./data";
import styles from "./style.module.scss";

const SvedeniyaStruktura = () => {
  const { title, info, collegial, docsTitle, docs } = SVEDENIYA_STRUKTURA;

  return (
    <>
      <SectionHeading title={title} />

      <InfoCard rows={info}>
        <div className={styles.collegial}>
          <div className={styles.collegialHead}>
            <PeopleIcon className={styles.collegialIcon} />
            <span className={styles.collegialTitle}>{collegial.title}</span>
          </div>
          <ul className={styles.collegialList}>
            {collegial.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </InfoCard>

      <DocsCard title={docsTitle} docs={docs} />
    </>
  );
};

export default SvedeniyaStruktura;
