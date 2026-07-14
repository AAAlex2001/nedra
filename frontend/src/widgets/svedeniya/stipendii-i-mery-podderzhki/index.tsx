import Card from "@/shared/ui/card";
import SectionHeading from "@/shared/ui/section-heading";
import { STIPENDII } from "./data";
import styles from "./style.module.scss";

const SvedeniyaStipendii = () => {
  const { title, note } = STIPENDII;

  return (
    <>
      <SectionHeading title={title} />

      <Card>
        <p className={styles.text}>
          {note.before}
          <strong className={styles.accent}>{note.accent}</strong>
          {note.after}
        </p>
      </Card>
    </>
  );
};

export default SvedeniyaStipendii;
