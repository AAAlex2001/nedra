import { buildMetadata } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import SectionHeading from "@/shared/ui/section-heading";
import SvedeniyaCards from "@/shared/ui/svedeniya-cards";
import styles from "./page.module.scss";

export const metadata = buildMetadata("/svedeniya");

export default function SvedeniyaIndexPage() {
  return (
    <main className={styles.page}>
      <Breadcrumbs
        items={[
          { label: "Главная", href: "/" },
          { label: "Сведения об образовательной организации" },
        ]}
      />

      <div className={styles.body}>
        <SectionHeading title="Сведения об образовательной организации" />
        <SvedeniyaCards />
      </div>
    </main>
  );
}
