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

const RING_RADIUS = 18;
const RING_LENGTH = 2 * Math.PI * RING_RADIUS;

const ContentsIcon = () => (
  <svg
    className={styles.icon}
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    aria-hidden="true"
  >
    <path d="M9 6h11M9 12h11M9 18h11" />
    <path d="M4 6h.01M4 12h.01M4 18h.01" strokeWidth="3" />
  </svg>
);

const ProgressRing = ({ progress }: { progress: number }) => (
  <svg className={styles.ring} viewBox="0 0 40 40" aria-hidden="true">
    <circle className={styles.ringTrack} cx="20" cy="20" r={RING_RADIUS} />
    <circle
      className={styles.ringValue}
      cx="20"
      cy="20"
      r={RING_RADIUS}
      strokeDasharray={RING_LENGTH}
      strokeDashoffset={RING_LENGTH * (1 - progress)}
    />
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
  const { open, popoverRef, show, leave, toggle, close } = useTocPopover();

  const activeIndex = items.findIndex((item) => item.id === activeId);
  const progress = (activeIndex + 1) / items.length;

  const selectAndClose = (event: MouseEvent<HTMLAnchorElement>, id: string) => {
    selectHeading(event, id);
    close();
  };

  return (
    <div ref={rootRef} className={styles.floatingAnchor}>
      <div
        ref={popoverRef}
        className={classNames(styles.floating, position.visible && styles.visible)}
        style={{ left: position.left }}
        aria-hidden={!position.visible}
        inert={!position.visible}
        onPointerEnter={show}
        onPointerLeave={leave}
      >
        <button
          type="button"
          className={classNames(styles.trigger, open && styles.triggerOpen)}
          aria-label={TITLE}
          aria-expanded={open}
          onClick={toggle}
        >
          <ProgressRing progress={progress} />
          <ContentsIcon />
        </button>

        {open && (
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
