import Card from "@/shared/ui/card";
import SectionHeading from "@/shared/ui/section-heading";
import { PITANIE } from "./data";
import styles from "./style.module.scss";

const SvedeniyaPitanie = () => {
  const { title, note } = PITANIE;

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

export default SvedeniyaPitanie;
