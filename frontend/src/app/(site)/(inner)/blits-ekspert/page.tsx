import type { ExpertCatalog } from "@/entities/expert";
import { hasSessionCookie } from "@/entities/user/api/session-server";
import { internalFetch } from "@/shared/api/server";
import { buildMetadata } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import SectionHeading from "@/shared/ui/section-heading";
import ExpertiseOrder from "@/widgets/expertise-order";
import styles from "./page.module.scss";

export const dynamic = "force-dynamic";

export const metadata = buildMetadata("/blits-ekspert");

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

export default async function BlitzExpertPage() {
  const catalog = await loadCatalog();
  const guest = !(await hasSessionCookie());

  return (
    <main className={styles.page}>
      <Breadcrumbs
        items={[
          { label: "Главная", href: "/" },
          { label: "Блиц-эксперт" },
        ]}
      />

      <div className={`${styles.body} ${guest ? styles.bodyGuest : ""}`}>
        <SectionHeading title="Блиц-эксперт" />
        <p className={styles.intro}>
          Экспертиза промышленной безопасности за 1–5 дней. Выберите, что проверяем, укажите
          класс опасности объекта и отрасль, приложите документацию. Заявку сразу увидят
          эксперты, аттестованные по вашей области.
        </p>

        <ExpertiseOrder catalog={catalog} />
      </div>
    </main>
  );
}
