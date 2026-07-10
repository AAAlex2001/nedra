import AccentLine from "@/shared/ui/accent-line";
import {
  ClockIcon,
  DirectorIcon,
  LocationIcon,
  MailIcon,
  PhoneIcon,
} from "@/shared/ui/icons";
import { CONTACTS_DATA } from "./data";
import styles from "./style.module.scss";

const mapSrc = `https://yandex.ru/map-widget/v1/?text=${encodeURIComponent(
  CONTACTS_DATA.mapQuery,
)}&z=16`;

const Contacts = () => {
  return (
    <section className={styles.section}>
      <div className={styles.bg} aria-hidden />
      <div className={styles.tint} aria-hidden />

      <div className={styles.map}>
        <iframe
          className={styles.mapFrame}
          src={mapSrc}
          title="Карта проезда — НПИ «Недра»"
          loading="lazy"
          allowFullScreen
        />
      </div>

      <div className={styles.content}>
        <div className={styles.heading}>
          <h2 className={styles.title}>{CONTACTS_DATA.title}</h2>
          <AccentLine width={30} />
        </div>

        <ul className={styles.list}>
          <li className={`${styles.row} ${styles.rowTop}`}>
            <DirectorIcon className={styles.icon} />
            <div className={styles.person}>
              <span className={styles.personLabel}>{CONTACTS_DATA.director.label}</span>
              <span className={styles.personName}>{CONTACTS_DATA.director.value}</span>
            </div>
          </li>

          <li className={styles.row}>
            <PhoneIcon className={styles.icon} />
            <a className={`${styles.text} ${styles.link}`} href={`tel:${CONTACTS_DATA.phoneHref}`}>
              {CONTACTS_DATA.phone}
            </a>
          </li>

          <li className={styles.row}>
            <MailIcon className={styles.icon} />
            <a className={`${styles.text} ${styles.link}`} href={`mailto:${CONTACTS_DATA.email}`}>
              {CONTACTS_DATA.email}
            </a>
          </li>

          <li className={`${styles.row} ${styles.rowTop}`}>
            <LocationIcon className={styles.icon} />
            <span className={styles.text}>{CONTACTS_DATA.address}</span>
          </li>

          <li className={styles.row}>
            <ClockIcon className={styles.icon} />
            <span className={styles.text}>{CONTACTS_DATA.schedule}</span>
          </li>
        </ul>
      </div>
    </section>
  );
};

export default Contacts;
