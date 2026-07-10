import { LocationIcon, MailIcon, PhoneIcon } from "@/shared/ui/icons";
import { CONTACTS_DATA } from "../contacts/data";
import { FOOTER_DATA } from "./data";
import styles from "./style.module.scss";

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.top}>
        <div className={styles.brand}>
          <div className={styles.logo}>
            <span className={styles.logoIcon} aria-hidden />
            <span className={styles.company}>{FOOTER_DATA.company}</span>
          </div>
          <p className={styles.description}>{FOOTER_DATA.description}</p>
        </div>

        <nav className={styles.nav}>
          <span className={styles.colTitle}>{FOOTER_DATA.navTitle}</span>
          <ul className={styles.navList}>
            {FOOTER_DATA.nav.map((item) => (
              <li key={item.label}>
                <a className={styles.navLink} href={item.href}>
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className={styles.contacts}>
          <span className={styles.colTitle}>{FOOTER_DATA.contactsTitle}</span>
          <ul className={styles.contactsList}>
            <li className={styles.row}>
              <PhoneIcon className={styles.icon} />
              <a className={styles.contactText} href={`tel:${CONTACTS_DATA.phoneHref}`}>
                {CONTACTS_DATA.phone}
              </a>
            </li>
            <li className={styles.row}>
              <MailIcon className={styles.icon} />
              <a className={styles.contactText} href={`mailto:${CONTACTS_DATA.email}`}>
                {CONTACTS_DATA.email}
              </a>
            </li>
            <li className={`${styles.row} ${styles.rowTop}`}>
              <LocationIcon className={styles.icon} />
              <span className={styles.contactText}>{CONTACTS_DATA.address}</span>
            </li>
          </ul>
        </div>
      </div>

      <div className={styles.bottom}>
        <span className={styles.copyright}>{FOOTER_DATA.copyright}</span>
        <a className={styles.privacy} href={FOOTER_DATA.privacy.href}>
          {FOOTER_DATA.privacy.label}
        </a>
      </div>
    </footer>
  );
};

export default Footer;
