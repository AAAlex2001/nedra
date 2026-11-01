import classNames from "classnames";
import Link from "next/link";
import {
  SECTION_PATH,
  SECTION_TITLE,
  articlePath,
  getLatestArticles,
  type ArticleCardData,
  type ArticleSection,
} from "@/entities/article";
import { COMPANY_CONTACTS } from "@/shared/config/company";
import { LEGAL_LINKS } from "@/shared/config/legal";
import ContactRow from "@/shared/ui/contact-row";
import { LocationIcon, MailIcon, NedraLogo, PhoneIcon } from "@/shared/ui/icons";
import {
  FOOTER_DATA,
  LATEST_ARTICLES_COUNT,
  MATERIALS_TITLE,
  SITE_GROUP,
  SVEDENIYA_GROUP,
  type FooterLinkGroup,
} from "./data";
import styles from "./style.module.scss";

type MaterialsSection = {
  section: ArticleSection;
  articles: ArticleCardData[];
};

const SitemapGroup = ({ group }: { group: FooterLinkGroup }) => (
  <nav
    className={classNames(styles.sitemapGroup, group.wide && styles.sitemapGroupWide)}
    aria-label={group.title}
  >
    <span className={styles.groupTitle}>{group.title}</span>
    <ul className={styles.navList}>
      {group.links.map((item) => (
        <li key={item.href}>
          <Link className={styles.navLink} href={item.href}>
            {item.label}
          </Link>
        </li>
      ))}
    </ul>
  </nav>
);

const MaterialsGroup = ({ sections }: { sections: MaterialsSection[] }) => (
  <nav className={styles.sitemapGroup} aria-label={MATERIALS_TITLE}>
    <span className={styles.groupTitle}>{MATERIALS_TITLE}</span>

    {sections.map(({ section, articles }) => (
      <div key={section} className={styles.materials}>
        <Link className={styles.navLink} href={SECTION_PATH[section]}>
          {SECTION_TITLE[section]}
        </Link>

        {articles.length > 0 && (
          <ul className={styles.articleList}>
            {articles.map((article) => (
              <li key={article.slug}>
                <Link className={styles.articleLink} href={articlePath(article)}>
                  {article.title}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    ))}
  </nav>
);

const Footer = async () => {
  const [blogArticles, newsArticles] = await Promise.all([
    getLatestArticles("blog", LATEST_ARTICLES_COUNT),
    getLatestArticles("news", LATEST_ARTICLES_COUNT),
  ]);

  const materials: MaterialsSection[] = [
    { section: "blog", articles: blogArticles },
    { section: "news", articles: newsArticles },
  ];

  return (
    <footer className={styles.footer}>
      <div className={styles.top}>
        <div className={styles.brand}>
          <Link
            className={styles.logo}
            href="/"
            aria-label="НПИ «Недра» — на главную"
          >
            <NedraLogo className={styles.logoIcon} />
          </Link>
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
          <SitemapGroup group={SITE_GROUP} />
          <MaterialsGroup sections={materials} />
          <SitemapGroup group={SVEDENIYA_GROUP} />
        </div>
      </div>

      <div className={styles.bottom}>
        <span className={styles.copyright}>{FOOTER_DATA.copyright}</span>
        <nav className={styles.legal} aria-label="Правовая информация">
          {LEGAL_LINKS.map((item) => (
            <Link key={item.href} className={styles.privacy} href={item.href}>
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </footer>
  );
};

export default Footer;
