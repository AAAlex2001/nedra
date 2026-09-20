"use client";

import { usePathname } from "next/navigation";
import { TabLinks } from "@/shared/ui/tabs";
import styles from "./style.module.scss";

type AdminNavProps = {
  basePath: string;
};

const findActive = (pathname: string, basePath: string): string => {
  if (pathname.startsWith(`${basePath}/articles`)) return "articles";
  if (pathname.startsWith(`${basePath}/experts`)) return "experts";
  if (pathname.startsWith(`${basePath}/expertises`)) return "expertises";
  if (pathname.startsWith(`${basePath}/tariffs`)) return "tariffs";

  return "requests";
};

const AdminNav = ({ basePath }: AdminNavProps) => {
  const pathname = usePathname();

  const items = [
    { key: "requests", label: "Заявки", href: basePath },
    { key: "articles", label: "Статьи", href: `${basePath}/articles` },
    { key: "experts", label: "Эксперты", href: `${basePath}/experts` },
    { key: "expertises", label: "Экспертизы", href: `${basePath}/expertises` },
    { key: "tariffs", label: "Тарифы", href: `${basePath}/tariffs` },
  ];

  return (
    <div className={styles.nav}>
      <TabLinks
        items={items}
        active={findActive(pathname, basePath)}
        label="Разделы админки"
        stretch
      />
    </div>
  );
};

export default AdminNav;
