"use client";

import { useEffect, useState } from "react";
import { BurgerIcon, CloseIcon, NedraLogo } from "@/shared/ui/icons";
import { HEADER_NAV } from "./data";
import BurgerMenu from "./ui/burger-menu";
import styles from "./style.module.scss";

const Header = () => {
  const [open, setOpen] = useState(false);
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    let lastY = window.scrollY;

    const onScroll = () => {
      const y = window.scrollY;
      if (y > lastY && y > 100) {
        setHidden(true);
      } else if (y < lastY) {
        setHidden(false);
      }
      lastY = y;
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <header
        className={`${styles.header} ${hidden && !open ? styles.hidden : ""}`}
      >
        <div className={styles.inner}>
          <a className={styles.logo} href="/" aria-label="НПИ «Недра» — на главную">
            <NedraLogo className={styles.logoIcon} />
          </a>

          <nav className={styles.tabs}>
            {HEADER_NAV.map((item) => (
              <a key={item.label} className={styles.tab} href={item.href}>
                {item.label}
              </a>
            ))}
          </nav>

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
      </header>

      <BurgerMenu open={open} nav={HEADER_NAV} onClose={() => setOpen(false)} />
    </>
  );
};

export default Header;
