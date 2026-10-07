import { getArticle, type ArticleCardData } from "@/entities/article";
import type { AuditChecklistItem } from "@/entities/expertise";
import { isAuditTariff, type Tariff } from "@/entities/tariff";
import { getCurrentUser } from "@/entities/user/api/session-server";
import { internalFetch } from "@/shared/api/server";
import { buildMetadata } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import SectionHeading from "@/shared/ui/section-heading";
import AuditOrder from "@/widgets/audit-order";
import BlitsAuditLanding, { ARTICLE_SLUGS } from "@/widgets/blits-audit";
import styles from "./page.module.scss";

export const dynamic = "force-dynamic";

export const metadata = buildMetadata("/blits-audit");

const loadChecklist = async (): Promise<AuditChecklistItem[]> => {
  try {
    const response = await internalFetch("/v1/audit/checklist", { cache: "no-store" });

    if (!response.ok) return [];

    const items: AuditChecklistItem[] = await response.json();

    return items;
  } catch {
    return [];
  }
};

const loadPrice = async (): Promise<string | null> => {
  try {
    const response = await internalFetch("/v1/tariffs", { cache: "no-store" });

    if (!response.ok) return null;

    const items: Tariff[] = await response.json();
    const tariff = items.find((item) => isAuditTariff(item));

    return tariff?.price ?? null;
  } catch {
    return null;
  }
};

const loadArticles = async (): Promise<ArticleCardData[]> => {
  const found = await Promise.all(ARTICLE_SLUGS.map((slug) => getArticle(slug)));

  return found.filter((article) => article !== null);
};

export default async function BlitzAuditPage() {
  const checklist = await loadChecklist();
  const user = await getCurrentUser();
  const showLanding = user === null || user.role === "expert";

  if (showLanding) {
    const price = await loadPrice();
    const articles = await loadArticles();

    return <BlitsAuditLanding checklist={checklist} price={price} articles={articles} />;
  }

  return (
    <main className={styles.page}>
      <Breadcrumbs
        items={[
          { label: "Главная", href: "/" },
          { label: "Блиц-аудит" },
        ]}
      />

      <div className={styles.body}>
        <SectionHeading title="Блиц-аудит" />
        <p className={styles.intro}>
          Аудит системы управления промышленной безопасностью по документам. Укажите объект
          аудита, предложите цену и загрузите документы по перечню — всё или только то, что
          есть. Заявку сразу увидят аудиторы.
        </p>

        <AuditOrder checklist={checklist} />
      </div>
    </main>
  );
}
