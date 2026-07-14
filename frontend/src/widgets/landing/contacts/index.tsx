import AccentLine from "@/shared/ui/accent-line";
import ContactRow from "@/shared/ui/contact-row";
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
    <section id="contacts" className={styles.section}>
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

        <address className={styles.list} style={{ fontStyle: "normal" }}>
          <div className={`${styles.row} ${styles.rowTop}`}>
            <DirectorIcon className={styles.icon} />
            <div className={styles.person}>
              <span className={styles.personLabel}>{CONTACTS_DATA.director.label}</span>
              <span className={styles.personName}>{CONTACTS_DATA.director.value}</span>
            </div>
          </div>

          <ContactRow icon={<PhoneIcon />} href={`tel:${CONTACTS_DATA.phoneHref}`}>
            {CONTACTS_DATA.phone}
          </ContactRow>
          <ContactRow icon={<MailIcon />} href={`mailto:${CONTACTS_DATA.email}`}>
            {CONTACTS_DATA.email}
          </ContactRow>
          <ContactRow icon={<LocationIcon />} align="top">
            {CONTACTS_DATA.address}
          </ContactRow>
          <ContactRow icon={<ClockIcon />}>{CONTACTS_DATA.schedule}</ContactRow>
        </address>
      </div>
    </section>
  );
};

export default Contacts;
