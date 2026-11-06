import Button from "@/shared/ui/button";
import OutlineButton from "@/shared/ui/outline-button";
import { DIRECTION_PRESENTATION } from "../../data";
import ServiceIcon from "../service-icon";
import styles from "../../style.module.scss";

const ServicesHero = () => (
  <header className={styles.hero}>
    <h1>Услуги НПИ «Недра»</h1>
    <p>
      Проектирование, экспертиза промышленной безопасности, аудит и исследования.
      Поможем решить задачу вашего объекта — от исходных данных до результата.
    </p>
    <div className={styles.heroActions}>
      <Button href="#request">Оставить заявку</Button>
      <OutlineButton href={`#direction-${DIRECTION_PRESENTATION[0].id}`}>
        Подробнее
      </OutlineButton>
    </div>

    <nav className={styles.navigation} aria-label="Направления услуг">
      {DIRECTION_PRESENTATION.map(({ id, label, icon }) => (
        <a key={id} href={`#direction-${id}`}>
          <span>{label}</span>
          <span className={styles.navigationIcon}>
            <ServiceIcon name={icon} />
          </span>
        </a>
      ))}
    </nav>
  </header>
);

export default ServicesHero;
