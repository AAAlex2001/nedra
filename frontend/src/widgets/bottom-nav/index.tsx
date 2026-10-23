"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useSession } from "@/entities/user";
import { useAuthModal } from "@/features/auth";
import { useCommissionPopup } from "@/features/commission-application";
import ServiceNavigation from "@/widgets/service-navigation";
import { UserCircleIcon, DocumentIcon, PeopleIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

export default function BottomNav() {
  const pathname = usePathname();
  const session = useSession();
  const { openModal } = useAuthModal();
  const { openForm } = useCommissionPopup();
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    let previous = window.scrollY;
    const onScroll = () => {
      const current = window.scrollY;
      if (Math.abs(current - previous) < 8 && current > 80) return;
      setCollapsed(current > 80 && current > previous);
      previous = current;
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const profile = <><UserCircleIcon /><span>Профиль</span></>;
  return (
    <>
      <div className={styles.spacer} aria-hidden="true" />
      <div className={`${styles.bar} ${collapsed ? styles.collapsed : ""}`}>
        <div className={styles.promo}><ServiceNavigation compact /></div>
        <nav className={styles.tabs} aria-label="Быстрые разделы">
          {session.user ? (
            <Link href="/kabinet" className={styles.tab} aria-current={pathname.startsWith("/kabinet") ? "page" : undefined}>{profile}</Link>
          ) : (
            <button type="button" className={styles.tab} onClick={openModal}>{profile}</button>
          )}
          <Link href="/blits-ekspert" className={`${styles.tab} ${styles.expert}`} aria-current={pathname.startsWith("/blits-ekspert") ? "page" : undefined}><svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m13 2-9 12h7l-1 8 10-13h-7l1-7Z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg><span>Блиц-эксперт</span></Link>
          <Link href="/blits-audit" className={styles.tab} aria-current={pathname.startsWith("/blits-audit") ? "page" : undefined}><DocumentIcon /><span>Блиц-аудит</span></Link>
          <button type="button" className={styles.tab} onClick={openForm} aria-haspopup="dialog"><PeopleIcon /><span>Комиссия</span></button>
        </nav>
      </div>
    </>
  );
}
