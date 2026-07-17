import { COMPANY_CONTACTS } from "@/shared/config/company";
import ContactRow from "@/shared/ui/contact-row";
import { LocationIcon, MailIcon, NedraLogo, PhoneIcon } from "@/shared/ui/icons";
import { FOOTER_DATA, FOOTER_SITEMAP } from "./data";
import styles from "./style.module.scss";

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.top}>
        <div className={styles.brand}>
          <a
            className={styles.logo}
            href="/"
            aria-label="НПИ «Недра» — на главную"
          >
            <NedraLogo className={styles.logoIcon} />
          </a>
          <p className={styles.description}>{FOOTER_DATA.description}</p>
        </div>

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

      <div className={styles.sitemap}>
        <span className={styles.sitemapTitle}>{FOOTER_DATA.sitemapTitle}</span>

        <div className={styles.sitemapGrid}>
          {FOOTER_SITEMAP.map((group) => (
            <nav
              key={group.title}
              className={`${styles.sitemapGroup} ${group.wide ? styles.sitemapGroupWide : ""}`}
              aria-label={group.title}
            >
              <span className={styles.groupTitle}>{group.title}</span>
              <ul className={styles.navList}>
                {group.links.map((item) => (
                  <li key={item.href}>
                    <a className={styles.navLink} href={item.href}>
                      {item.label}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          ))}
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
