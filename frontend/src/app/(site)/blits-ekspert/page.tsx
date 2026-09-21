import { getArticles, type ArticleCardData } from "@/entities/article";
import type { ExpertCatalog } from "@/entities/expert";
import type { Tariff } from "@/entities/tariff";
import { getCurrentUser } from "@/entities/user/api/session-server";
import { internalFetch } from "@/shared/api/server";
import { buildMetadata } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import SectionHeading from "@/shared/ui/section-heading";
import BlitsEkspertLanding, { ARTICLE_SLUGS } from "@/widgets/blits-ekspert";
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

const loadTariffs = async (): Promise<Tariff[]> => {
  try {
    const response = await internalFetch("/v1/tariffs", { cache: "no-store" });

    if (!response.ok) return [];

    const items: Tariff[] = await response.json();

    return items;
  } catch {
    return [];
  }
};

const loadArticles = async (): Promise<ArticleCardData[]> => {
  const { articles } = await getArticles({
    section: "news",
    tag: "Промышленная безопасность",
    page: 10,
  });

  const picked = ARTICLE_SLUGS.flatMap((slug) =>
    articles.filter((article) => article.slug === slug),
  );

  return picked.length > 0 ? picked : articles.slice(0, ARTICLE_SLUGS.length);
};

export default async function BlitzExpertPage() {
  const catalog = await loadCatalog();
  const user = await getCurrentUser();
  const showLanding = user === null || user.role === "expert";

  if (showLanding) {
    const tariffs = await loadTariffs();
    const articles = await loadArticles();

    return <BlitsEkspertLanding catalog={catalog} tariffs={tariffs} articles={articles} />;
  }

  return (
    <main className={styles.page}>
      <Breadcrumbs
        items={[
          { label: "Главная", href: "/" },
          { label: "Блиц-эксперт" },
        ]}
      />

      <div className={styles.body}>
        <SectionHeading title="Блиц-эксперт" />
        <p className={styles.intro}>
          Экспертиза промышленной безопасности от 1 дня. Выберите, что проверяем, укажите
          класс опасности объекта и отрасль, приложите документацию. Заявку сразу увидят
          эксперты, аттестованные по вашей области.
        </p>

        <ExpertiseOrder catalog={catalog} />
      </div>
    </main>
  );
}
