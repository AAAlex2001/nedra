"use client";

import classNames from "classnames";
import type { MouseEvent } from "react";
import type { TocItem } from "@/entities/article";
import { ChevronIcon } from "@/shared/ui/icons";
import { useActiveHeading } from "../../model/use-active-heading";
import { useFloatingPosition } from "../../model/use-floating-position";
import { useTocPopover } from "../../model/use-toc-popover";
import styles from "./style.module.scss";

type ArticleTocProps = {
  items: TocItem[];
  variant: "collapsible" | "floating";
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

const ContentsIcon = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <rect x="4" y="3" width="16" height="18" rx="3" />
    <path d="M9 3v18M12.5 8h4M12.5 12h4M12.5 16h2.5" />
  </svg>
);

const CollapsibleToc = ({ items }: { items: TocItem[] }) => {
  const { activeId, selectHeading } = useActiveHeading(items);

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
};

const FloatingToc = ({ items }: { items: TocItem[] }) => {
  const { activeId, selectHeading } = useActiveHeading(items);
  const { rootRef, position } = useFloatingPosition();
  const popover = useTocPopover();

  const selectAndClose = (event: MouseEvent<HTMLAnchorElement>, id: string) => {
    selectHeading(event, id);
    popover.close();
  };

  return (
    <div ref={rootRef} className={styles.floatingAnchor}>
      <div
        ref={popover.popoverRef}
        className={classNames(styles.floating, position.visible && styles.visible)}
        style={{ left: position.left }}
        aria-hidden={!position.visible}
        inert={!position.visible}
        onPointerEnter={popover.show}
        onPointerLeave={popover.leave}
      >
        <button
          type="button"
          className={classNames(styles.trigger, popover.open && styles.triggerOpen)}
          aria-label={TITLE}
          aria-expanded={popover.open}
          onClick={popover.toggle}
        >
          <ContentsIcon />
        </button>

        {popover.open && (
          <nav className={styles.popover} aria-label={TITLE}>
            <p className={styles.popoverTitle}>{TITLE}</p>
            <TocList items={items} activeId={activeId} onSelect={selectAndClose} />
          </nav>
        )}
      </div>
    </div>
  );
};

const ArticleToc = ({ items, variant }: ArticleTocProps) =>
  variant === "collapsible" ? <CollapsibleToc items={items} /> : <FloatingToc items={items} />;

export default ArticleToc;
