"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useSession } from "@/entities/user";
import { useAuthModal } from "@/features/auth";
import { useCommissionPopup } from "@/features/commission-application";
import ServiceNavigation from "@/widgets/service-navigation";
import styles from "./style.module.scss";

export default function BottomNav() {
  const pathname = usePathname();
  const session = useSession();
  const { openModal } = useAuthModal();
  const { openForm } = useCommissionPopup();
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    let previous = Math.max(0, window.scrollY);
    let distance = 0;
    let direction = 0;
    let frame = 0;
    const onScroll = () => {
      if (frame) return;
      frame = requestAnimationFrame(() => {
        frame = 0;
        const current = Math.max(
          0,
          Math.min(window.scrollY, document.documentElement.scrollHeight - window.innerHeight),
        );
        const delta = current - previous;
        previous = current;
        if (current < 64) {
          setCollapsed(false);
          distance = 0;
          return;
        }
        if (Math.abs(delta) < 2) return;
        const nextDirection = Math.sign(delta);
        if (direction !== nextDirection) distance = 0;
        direction = nextDirection;
        distance += Math.abs(delta);
        if (distance >= (direction > 0 ? 56 : 32)) {
          setCollapsed(direction > 0);
          distance = 0;
        }
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      cancelAnimationFrame(frame);
    };
  }, []);

  const profile = (
    <>
      <NavIcon type="profile" />
      <span>Профиль</span>
    </>
  );
  return (
    <>
      <div className={styles.spacer} aria-hidden="true" />
      <div className={`${styles.bar} ${collapsed ? styles.collapsed : ""}`}>
        <div className={styles.promo} inert={collapsed}>
          <div className={styles.promoInner}>
            <ServiceNavigation compact />
          </div>
        </div>
        <nav className={styles.tabs} aria-label="Быстрые разделы">
          {session.user ? (
            <Link
              href="/kabinet"
              className={styles.tab}
              aria-current={pathname.startsWith("/kabinet") ? "page" : undefined}
            >
              {profile}
            </Link>
          ) : (
            <button type="button" className={styles.tab} onClick={openModal}>
              {profile}
            </button>
          )}
          <Link
            href="/blits-ekspert"
            className={`${styles.tab} ${styles.expert}`}
            aria-current={pathname.startsWith("/blits-ekspert") ? "page" : undefined}
          >
            <NavIcon type="expert" />
            <span>Блиц-эксперт</span>
          </Link>
          <Link
            href="/blits-audit"
            className={`${styles.tab} ${styles.audit}`}
            aria-current={pathname.startsWith("/blits-audit") ? "page" : undefined}
          >
            <NavIcon type="audit" />
            <span>Блиц-аудит</span>
          </Link>
          <button type="button" className={styles.tab} onClick={openForm} aria-haspopup="dialog">
            <NavIcon type="commission" />
            <span>Комиссия</span>
          </button>
        </nav>
      </div>
    </>
  );
}

function NavIcon({ type }: { type: "profile" | "expert" | "audit" | "commission" }) {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {type === "profile" && (
        <>
          <circle cx="12" cy="8" r="3.5" />
          <path d="M5 21v-2a7 7 0 0 1 14 0v2" />
        </>
      )}
      {type === "expert" && (
        <>
          <path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z" />
          <path d="m8.5 12 2.5 2.5 4.5-5" />
        </>
      )}
      {type === "audit" && (
        <>
          <rect x="5" y="5" width="14" height="16" rx="2" />
          <rect x="9" y="3" width="6" height="4" rx="1" />
          <path d="m8 12 1 1 2-2m2 1h3m-8 5 1 1 2-2m2 1h3" />
        </>
      )}
      {type === "commission" && (
        <>
          <circle cx="9" cy="8" r="3" />
          <path d="M3 21v-2a6 6 0 0 1 12 0v2m1-16a3 3 0 0 1 0 6m2 3a5 5 0 0 1 3 5v2" />
        </>
      )}
    </svg>
  );
}
