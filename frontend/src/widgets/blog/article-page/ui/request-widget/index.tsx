import { DIRECTION_OPTIONS } from "@/entities/service";
import { CompactRequestForm } from "@/features/request-form";
import styles from "./style.module.scss";

const RequestWidget = () => (
  <section className={styles.widget} aria-label="Заявка на работы">
    <p className={styles.title}>Оставьте заявку</p>
    <p className={styles.text}>
      Экспертиза, проектирование, изыскания — подберём исполнителя под вашу задачу
    </p>

    <CompactRequestForm directions={DIRECTION_OPTIONS} />
  </section>
);

export default RequestWidget;
