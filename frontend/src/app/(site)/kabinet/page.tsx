import type { Metadata } from "next";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import SectionHeading from "@/shared/ui/section-heading";
import Cabinet from "@/widgets/cabinet";
import styles from "./page.module.scss";

export const metadata: Metadata = {
  title: "Личный кабинет",
  robots: { index: false, follow: false },
};

export default function CabinetPage() {
  return (
    <main className={styles.page}>
      <Breadcrumbs
        items={[
          { label: "Главная", href: "/" },
          { label: "Личный кабинет" },
        ]}
      />

      <div className={styles.body}>
        <SectionHeading title="Личный кабинет" />
        <Cabinet />
      </div>
    </main>
  );
}
