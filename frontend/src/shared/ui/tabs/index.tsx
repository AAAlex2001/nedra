import Link from "next/link";
import styles from "./style.module.scss";

type TabItem = {
  key: string;
  label: string;
};

type TabLinkItem = {
  key: string;
  label: string;
  href: string;
};

type TabsProps = {
  items: TabItem[];
  active: string;
  onSelect: (key: string) => void;
  label: string;
};

type TabLinksProps = {
  items: TabLinkItem[];
  active: string;
  label: string;
};

export const Tabs = ({ items, active, onSelect, label }: TabsProps) => (
  <div className={styles.tabs} role="tablist" aria-label={label}>
    {items.map((item) => (
      <button
        key={item.key}
        type="button"
        role="tab"
        aria-selected={active === item.key}
        className={`${styles.tab} ${active === item.key ? styles.tabActive : ""}`}
        onClick={() => onSelect(item.key)}
      >
        {item.label}
      </button>
    ))}
  </div>
);

export const TabLinks = ({ items, active, label }: TabLinksProps) => (
  <nav className={styles.tabs} aria-label={label}>
    {items.map((item) => (
      <Link
        key={item.key}
        href={item.href}
        aria-current={active === item.key ? "page" : undefined}
        className={`${styles.tab} ${active === item.key ? styles.tabActive : ""}`}
      >
        {item.label}
      </Link>
    ))}
  </nav>
);
