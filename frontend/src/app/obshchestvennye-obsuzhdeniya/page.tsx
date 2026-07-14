import type { Metadata } from "next";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import SectionHeading from "@/shared/ui/section-heading";
import ObshchestvennyeObsuzhdeniya from "@/widgets/obshchestvennye-obsuzhdeniya";
import styles from "./page.module.scss";

export const metadata: Metadata = {
  title: "Общественные обсуждения | НПИ «Недра»",
};

export default function ObshchestvennyeObsuzhdeniyaPage() {
  return (
    <main className={styles.page}>
      <Breadcrumbs
        items={[
          { label: "Главная", href: "/" },
          { label: "Общественные обсуждения" },
        ]}
      />

      <div className={styles.body}>
        <SectionHeading title="Общественные обсуждения" />
        <ObshchestvennyeObsuzhdeniya />
      </div>
    </main>
  );
}
