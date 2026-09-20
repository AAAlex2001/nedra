import type { ExpertCatalog } from "@/entities/expert";
import { internalFetch } from "@/shared/api/server";
import { buildMetadata } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import SectionHeading from "@/shared/ui/section-heading";
import ExpertApplicationSection from "@/widgets/expert-application";
import styles from "./page.module.scss";

export const dynamic = "force-dynamic";

export const metadata = buildMetadata("/registratsiya-eksperta");

const loadCatalog = async (): Promise<ExpertCatalog | null> => {
  try {
    const response = await internalFetch("/v1/experts/catalog", { cache: "no-store" });

    if (!response.ok) return null;

    const catalog: ExpertCatalog = await response.json();

    return catalog;
  } catch {
    return null;
  }
};

export default async function ExpertApplicationPage() {
  const catalog = await loadCatalog();

  return (
    <main className={styles.page}>
      <Breadcrumbs
        items={[
          { label: "Главная", href: "/" },
          { label: "Регистрация эксперта" },
        ]}
      />

      <div className={styles.body}>
        <SectionHeading title="Регистрация эксперта" />
        <ExpertApplicationSection catalog={catalog} />
      </div>
    </main>
  );
}
