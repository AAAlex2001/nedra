"use client";

import Image from "next/image";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useSession } from "@/entities/user";
import Button from "@/shared/ui/button";
import styles from "./style.module.scss";

const HIDDEN_ON = ["/blits-ekspert", "/kabinet"];

const SCROLL_BEFORE_SHOW = 160;

const GuestBar = () => {
  const { status } = useSession();
  const pathname = usePathname();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const check = () => {
      setVisible(window.scrollY > SCROLL_BEFORE_SHOW);
    };

    check();
    window.addEventListener("scroll", check, { passive: true });

    return () => window.removeEventListener("scroll", check);
  }, []);

  if (status !== "anonymous") return null;
  if (HIDDEN_ON.some((path) => pathname.startsWith(path))) return null;

  return (
    <>
      <div className={styles.spacer} aria-hidden="true" />

      <aside className={`${styles.bar} ${visible ? styles.barVisible : ""}`} aria-hidden={!visible}>
        <Image className={styles.icon} src="/blitz/20.webp" alt="" width={120} height={120} />

        <div className={styles.text}>
          <span className={styles.title}>
            БЛИЦ-ЭКСПЕРТ – онлайн экспертиза промышленной безопасности!
          </span>
          <span className={styles.subtitle}>Загрузите файл – получите заключение с ЭЦП!</span>
        </div>

        <Button className={styles.button} href="/blits-ekspert">
          Узнать стоимость
        </Button>
      </aside>
    </>
  );
};

export default GuestBar;
