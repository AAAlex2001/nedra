import Card from "@/shared/ui/card";
import { AddUserIcon } from "@/shared/ui/icons";
import NoteRow from "@/shared/ui/note-row";
import SectionHeading from "@/shared/ui/section-heading";
import { FINANSOVO } from "./data";
import styles from "./style.module.scss";

const SvedeniyaFinansovo = () => {
  const { title, note, sourcesTitle, sources } = FINANSOVO;

  return (
    <>
      <SectionHeading title={title} />

      <Card gap={10}>
        <NoteRow icon={<AddUserIcon />} divider>
          {note}
        </NoteRow>

        <div className={styles.sources}>
          <h2 className={styles.sourcesTitle}>{sourcesTitle}</h2>

          {sources.map((source) => (
            <div key={source.code} className={styles.source}>
              <div className={styles.head}>
                <span className={styles.number}>{source.code}.</span>
                <span className={styles.sourceTitle}>{source.title}</span>
              </div>

              <p className={styles.intro}>{source.intro}</p>

              <ul className={styles.list}>
                {source.bullets.map((bullet, index) => (
                  <li key={index}>{bullet}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </Card>
    </>
  );
};

export default SvedeniyaFinansovo;
