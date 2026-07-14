import { Fragment } from "react";
import styles from "./style.module.scss";

export type Crumb = {
  label: string;
  href?: string;
};

type BreadcrumbsProps = {
  items: Crumb[];
};

const Chevron = () => (
  <svg
    className={styles.arrow}
    width="15"
    height="15"
    viewBox="0 0 15 15"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path
      d="M5.75 3.5L9.75 7.5L5.75 11.5"
      stroke="#B8BBC2"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const Breadcrumbs = ({ items }: BreadcrumbsProps) => (
  <nav className={styles.breadcrumbs} aria-label="Хлебные крошки">
    {items.map((item, index) => {
      const isLast = index === items.length - 1;

      return (
        <Fragment key={`${item.label}-${index}`}>
          {item.href && !isLast ? (
            <a className={styles.crumb} href={item.href}>
              {item.label}
            </a>
          ) : (
            <span
              className={`${styles.crumb} ${isLast ? styles.current : ""}`}
              aria-current={isLast ? "page" : undefined}
            >
              {item.label}
            </span>
          )}
          {!isLast && <Chevron />}
        </Fragment>
      );
    })}
  </nav>
);

export default Breadcrumbs;
