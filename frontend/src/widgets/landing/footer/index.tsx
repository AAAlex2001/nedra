import { COMPANY_CONTACTS } from "@/shared/config/company";
import ContactRow from "@/shared/ui/contact-row";
import { LocationIcon, MailIcon, PhoneIcon } from "@/shared/ui/icons";
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
          <div className={styles.contactsList}>
            <ContactRow icon={<PhoneIcon />} href={`tel:${COMPANY_CONTACTS.phoneHref}`}>
              {COMPANY_CONTACTS.phone}
            </ContactRow>
            <ContactRow icon={<MailIcon />} href={`mailto:${COMPANY_CONTACTS.email}`}>
              {COMPANY_CONTACTS.email}
            </ContactRow>
            <ContactRow icon={<LocationIcon />} align="top">
              {COMPANY_CONTACTS.address}
            </ContactRow>
          </div>
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
