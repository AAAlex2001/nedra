import { SVEDENIYA_BASE, SVEDENIYA_SECTIONS } from "./data";
import styles from "./style.module.scss";

type SvedeniyaNavProps = {
  activeSlug: string;
};

const SvedeniyaNav = ({ activeSlug }: SvedeniyaNavProps) => (
  <nav
    className={styles.nav}
    aria-label="Сведения об образовательной организации"
  >
    {SVEDENIYA_SECTIONS.map((section) => {
      const isActive = section.slug === activeSlug;
      return (
        <a
          key={section.slug}
          className={`${styles.pill} ${isActive ? styles.active : ""}`}
          href={`${SVEDENIYA_BASE}/${section.slug}`}
          aria-current={isActive ? "page" : undefined}
        >
          {section.label}
        </a>
      );
    })}
  </nav>
);

export default SvedeniyaNav;
