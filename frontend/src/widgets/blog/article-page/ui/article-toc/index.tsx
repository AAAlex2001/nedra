"use client";

import classNames from "classnames";
import type { MouseEvent } from "react";
import type { TocItem } from "@/entities/article";
import { ChevronIcon } from "@/shared/ui/icons";
import { useActiveHeading } from "../../model/use-active-heading";
import styles from "./style.module.scss";

type ArticleTocProps = {
  items: TocItem[];
  variant: "collapsible" | "card";
};

type TocListProps = {
  items: TocItem[];
  activeId: string;
  onSelect: (event: MouseEvent<HTMLAnchorElement>, id: string) => void;
};

const TITLE = "Содержание";

const TocList = ({ items, activeId, onSelect }: TocListProps) => (
  <ol className={styles.list}>
    {items.map((item) => {
      const active = item.id === activeId;

      return (
        <li key={item.id}>
          <a
            href={`#${item.id}`}
            className={classNames(styles.link, active && styles.active)}
            aria-current={active ? "location" : undefined}
            onClick={(event) => onSelect(event, item.id)}
          >
            {item.title}
          </a>
        </li>
      );
    })}
  </ol>
);

const ArticleToc = ({ items, variant }: ArticleTocProps) => {
  const { activeId, selectHeading } = useActiveHeading(items);

  if (variant === "collapsible") {
    return (
      <details className={styles.collapsible}>
        <summary className={styles.summary}>
          <span>{TITLE}</span>
          <ChevronIcon className={styles.chevron} />
        </summary>
        <nav className={styles.panel} aria-label={TITLE}>
          <TocList items={items} activeId={activeId} onSelect={selectHeading} />
        </nav>
      </details>
    );
  }

  return (
    <nav className={styles.card} aria-label={TITLE}>
      <p className={styles.title}>{TITLE}</p>
      <TocList items={items} activeId={activeId} onSelect={selectHeading} />
    </nav>
  );
};

export default ArticleToc;
