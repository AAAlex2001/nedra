import { buildMetadata } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import SectionHeading from "@/shared/ui/section-heading";
import RequestSection from "@/widgets/landing/request-form";
import ObshchestvennyeObsuzhdeniya from "@/widgets/obshchestvennye-obsuzhdeniya";
import styles from "./page.module.scss";

export const metadata = buildMetadata("/obshchestvennye-obsuzhdeniya");

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

      <RequestSection />
    </main>
  );
}
