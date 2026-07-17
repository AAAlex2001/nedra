"use client";

import Link from "next/link";
import { useState } from "react";
import { BurgerIcon, CloseIcon, NedraLogo } from "@/shared/ui/icons";
import { HEADER_NAV } from "./data";
import BurgerMenu from "./ui/burger-menu";
import styles from "./style.module.scss";

const Header = () => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <header className={styles.header}>
        <div className={styles.inner}>
          <Link className={styles.logo} href="/" aria-label="НПИ «Недра» — на главную">
            <NedraLogo className={styles.logoIcon} />
          </Link>

          <nav className={styles.tabs}>
            {HEADER_NAV.map((item) => (
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
