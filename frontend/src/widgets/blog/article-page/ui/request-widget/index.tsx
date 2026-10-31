import { DIRECTION_OPTIONS } from "@/entities/service";
import { CompactRequestForm } from "@/features/request-form";
import styles from "./style.module.scss";

const RequestWidget = () => (
  <section className={styles.widget} aria-label="Заявка на работы">
    <p className={styles.title}>Оставьте заявку</p>
    <p className={styles.text}>
      Проведём экспертизу, проектирование, изыскания и другие работы — подберём исполнителя
      под вашу задачу
    </p>

    <div className={styles.card}>
      <CompactRequestForm directions={DIRECTION_OPTIONS} />
    </div>
  </section>
);

export default RequestWidget;
