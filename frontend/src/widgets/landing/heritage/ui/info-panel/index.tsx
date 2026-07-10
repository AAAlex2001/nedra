import type { InfoPanel } from "../../data";
import styles from "./style.module.scss";

type InfoPanelsProps = {
  panels: InfoPanel[];
};

const InfoPanels = ({ panels }: InfoPanelsProps) => {
  const [servicesPanel, staffPanel] = panels;

  return (
    <div className={styles.row}>
      <article className={styles.card}>
        <div className={styles.titleRow}>
          <h3 className={styles.title}>{servicesPanel.title}</h3>
        </div>
        <ul className={styles.list}>
          {servicesPanel.items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </article>

      <article className={styles.card}>
        <p className={styles.intro}>{staffPanel.text}</p>
        <ul className={styles.list}>
          {staffPanel.items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </article>
    </div>
  );
};

export default InfoPanels;
