import AccentLine from "@/shared/ui/accent-line";
import { INSTITUTE_DATA } from "./data";
import styles from "./style.module.scss";

const Institute = () => {
  return (
    <section className={styles.section}>
      <div className={styles.row}>
        <div className={styles.content}>
          <h2 className={styles.title}>
            <span className={styles.titleAccent}>{INSTITUTE_DATA.title}</span>
          </h2>
          <AccentLine width={30} />
          <ul className={styles.list}>
            {INSTITUTE_DATA.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <img
          className={styles.photo}
          src={INSTITUTE_DATA.photo}
          alt="Специалисты НПИ «Недра» на объекте"
        />
      </div>

      <img
        className={styles.diploma}
        src={INSTITUTE_DATA.diploma}
        alt="Диплом конкурса «Лучший экспонат»"
      />
    </section>
  );
};

export default Institute;
