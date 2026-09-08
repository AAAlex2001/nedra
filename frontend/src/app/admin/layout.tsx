import type { Metadata } from "next";
import Link from "next/link";
import { adminBasePath } from "@/shared/api/server";
import styles from "./layout.module.scss";

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const basePath = adminBasePath();

  return (
    <div className={styles.admin}>
      <nav className={styles.nav} aria-label="Разделы админки">
        <span className={styles.brand}>Админка</span>
        <Link href={basePath} className={styles.link}>
          Заявки
        </Link>
        <Link href={`${basePath}/articles`} className={styles.link}>
          Статьи
        </Link>
        <Link href="/blog" target="_blank" className={styles.external}>
          Блог на сайте ↗
        </Link>
      </nav>

      {children}
    </div>
  );
}
