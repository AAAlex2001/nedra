"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useSession } from "@/entities/user";
import styles from "./style.module.scss";

const SERVICES = [
  {
    href: "/blits-ekspert",
    name: "Блиц-эксперт",
    caption: "Онлайн экспертиза",
    image: "/blitz/20.webp",
    tone: "expert",
    action: "Рассчитать",
  },
  {
    href: "/blits-audit",
    name: "Блиц-аудит",
    caption: "Аудит безопасности",
    image: "/audit/1.webp",
    tone: "audit",
    action: "Открыть",
  },
];

export default function GuestBar() {
  const { status } = useSession();
  const pathname = usePathname();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY >= 150);

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    return () => window.removeEventListener("scroll", onScroll);
  }, [pathname]);
  const hiddenPaths = ["/blits-ekspert", "/blits-audit", "/kabinet"];
  const hiddenOnPage = hiddenPaths.some(
    (path) => pathname === path || pathname.startsWith(`${path}/`),
  );

  if (status !== "anonymous" || hiddenOnPage) return null;

  return (
    <>
      <div className={styles.spacer} aria-hidden="true" />
      <aside
        className={`${styles.bar} ${visible ? styles.visible : ""}`}
        aria-label="Онлайн-сервисы НПИ «Недра»"
        inert={!visible}
        aria-hidden={!visible}
      >
        {SERVICES.map((service) => (
          <div key={service.href} className={`${styles.item} ${styles[service.tone]}`}>
            <Link href={service.href} className={styles.text}>
              <Image
                className={styles.artwork}
                src={service.image}
                alt=""
                width={52}
                height={52}
                sizes="52px"
              />
              <span className={styles.copy}>
                <span className={styles.title}>{service.name}</span>
                <span className={styles.caption}>{service.caption}</span>
              </span>
            </Link>
            <Link
              href={service.href}
              className={styles.pill}
              aria-label={`${service.action}: ${service.name}`}
            >
              {service.action}
            </Link>
          </div>
        ))}
      </aside>
    </>
  );
}
