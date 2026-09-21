"use client";

import Image from "next/image";
import { usePathname } from "next/navigation";
import { useSession } from "@/entities/user";
import Button from "@/shared/ui/button";
import styles from "./style.module.scss";

const HIDDEN_ON = ["/blits-ekspert", "/kabinet"];

const GuestBar = () => {
  const { status } = useSession();
  const pathname = usePathname();

  if (status !== "anonymous") return null;
  if (HIDDEN_ON.some((path) => pathname.startsWith(path))) return null;

  return (
    <>
      <div className={styles.spacer} aria-hidden="true" />

      <aside className={styles.bar}>
        <Image className={styles.icon} src="/blitz/20.png" alt="" width={120} height={120} />

        <div className={styles.text}>
          <span className={styles.title}>Экспертиза промышленной безопасности от 1 дня</span>
          <span className={styles.subtitle}>
            Цена только за экспертизу, сроки продиктованы опытом штатных экспертов,
            заключение с ЭЦП, любая форма оплаты, работаем по гарантийному письму!
          </span>
        </div>

        <Button className={styles.button} href="/blits-ekspert">
          Узнать стоимость
        </Button>
      </aside>
    </>
  );
};

export default GuestBar;
