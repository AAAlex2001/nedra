"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { BurgerIcon, CloseIcon, NedraLogo } from "@/shared/ui/icons";
import { DESKTOP_NAV, HEADER_NAV } from "./data";
import BurgerMenu from "./ui/burger-menu";
import styles from "./style.module.scss";

const Header = () => {
  const [open, setOpen] = useState(false);
  const [activeGroup, setActiveGroup] = useState<string | null>(null);
  const navRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!activeGroup) return;

    const onPointerDown = (event: PointerEvent) => {
      if (!navRef.current?.contains(event.target as Node)) setActiveGroup(null);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      const trigger = document.getElementById(`header-trigger-${activeGroup}`);
      if (navRef.current?.contains(document.activeElement)) trigger?.focus();
      setActiveGroup(null);
    };

    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [activeGroup]);

  return (
    <>
      <header className={styles.header}>
        <div className={styles.inner}>
          <Link className={styles.logo} href="/" aria-label="НПИ «Недра» — на главную">
            <NedraLogo className={styles.logoIcon} />
          </Link>

          <nav className={styles.tabs} ref={navRef} aria-label="Основная навигация">
            {DESKTOP_NAV.map((item) => "children" in item ? (
              <div
                key={item.id}
                className={styles.group}
                onMouseEnter={() => setActiveGroup(item.id)}
                onMouseLeave={() => setActiveGroup(null)}
                onBlur={(event) => {
                  if (!event.currentTarget.contains(event.relatedTarget)) setActiveGroup(null);
                }}
              >
                <button
                  id={`header-trigger-${item.id}`}
                  type="button"
                  className={`${styles.tab} ${activeGroup === item.id ? styles.active : ""}`}
                  aria-expanded={activeGroup === item.id}
                  aria-controls={`header-panel-${item.id}`}
                  onClick={() => setActiveGroup((current) => current === item.id ? null : item.id)}
                  onKeyDown={(event) => {
                    if (event.key === "ArrowDown") {
                      event.preventDefault();
                      setActiveGroup(item.id);
                      requestAnimationFrame(() => {
                        document.getElementById(`header-panel-${item.id}`)?.querySelector("a")?.focus();
                      });
                    }
                  }}
                >
                  {item.label}
                  <svg className={styles.chevron} width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                    <path d="m4 6 4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </button>
                <div id={`header-panel-${item.id}`} className={styles.dropdown} hidden={activeGroup !== item.id}>
                  <div className={styles.dropdownPanel}>
                    {item.children.map((child) => (
                      <Link key={child.href} className={styles.dropdownLink} href={child.href} onClick={() => setActiveGroup(null)}>
                        <span className={styles.dropdownTitle}>{child.label}</span>
                        <span className={styles.dropdownDescription}>{child.description}</span>
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <Link key={item.label} className={styles.tab} href={item.href}>
                {item.label}
              </Link>
            ))}
          </nav>

          <div className={styles.controls}>
            <Link className={styles.contactChip} href="/#contacts">
              Контакты
            </Link>

            <button
              type="button"
              className={styles.burger}
              aria-label={open ? "Закрыть меню" : "Открыть меню"}
              aria-expanded={open}
              onClick={() => setOpen((value) => !value)}
            >
              {open ? (
                <CloseIcon className={styles.burgerIcon} />
              ) : (
                <BurgerIcon className={styles.burgerIcon} />
              )}
            </button>
          </div>
        </div>
      </header>

      <BurgerMenu
        open={open}
        nav={HEADER_NAV.filter((item) => item.label !== "Контакты")}
        onClose={() => setOpen(false)}
      />
    </>
  );
};

export default Header;
