import Card from "@/shared/ui/card";
import DocsCard from "@/shared/ui/docs-card";
import { GraduationCapIcon, ProcedureDocumentIcon } from "@/shared/ui/icons";
import NoteRow from "@/shared/ui/note-row";
import SectionHeading from "@/shared/ui/section-heading";
import { PLATNYE } from "./data";
import styles from "./style.module.scss";

const SvedeniyaPlatnye = () => {
  const { title, note, procedure, docsTitle, docs } = PLATNYE;

  return (
    <>
      <SectionHeading title={title} />

      <Card gap={10}>
        <NoteRow icon={<GraduationCapIcon />} divider>
          {note}
        </NoteRow>

        <div className={styles.procedure}>
          <span className={styles.icon}>
            <ProcedureDocumentIcon />
          </span>

          <div className={styles.content}>
            <p className={styles.title}>{procedure.title}</p>
            <p className={styles.text}>
              {procedure.textBefore}
              <strong className={styles.highlight}>{procedure.highlight}</strong>
              {procedure.textAfter}
            </p>
          </div>
        </div>
      </Card>

      <DocsCard title={docsTitle} docs={docs} />
    </>
  );
};

export default SvedeniyaPlatnye;
