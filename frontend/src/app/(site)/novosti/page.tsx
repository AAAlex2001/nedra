import { getArticles, getTags } from "@/entities/article";
import { buildMetadata } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import ArticlesHeading from "@/widgets/blog/articles-heading";
import ArticlesList from "@/widgets/blog/articles-list";
import RequestSection from "@/widgets/landing/request-form";
import styles from "../articles-page.module.scss";

export const dynamic = "force-dynamic";

export const metadata = buildMetadata("/novosti");

type SearchParams = Promise<{ tag?: string; page?: string; q?: string }>;

export default async function NewsPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const { tag, page, q } = await searchParams;
  const pageNumber = Math.max(1, Number(page) || 1);
  const search = q?.trim() ?? "";

  const [list, tags] = await Promise.all([
    getArticles({ section: "news", tag, search, page: pageNumber }),
    getTags("news"),
  ]);

  return (
    <>
      <main className={styles.page}>
        <Breadcrumbs items={[{ label: "Главная", href: "/" }, { label: "Новости" }]} />

        <div className={styles.body}>
          <ArticlesHeading
            title="Новости"
            subtitle="Изменения законодательства, новые требования Ростехнадзора, практика проектирования, экспертизы и экологии — коротко и по делу"
            total={list.total}
          />

          <ArticlesList
            section="news"
            list={list}
            tags={tags}
            activeTag={tag ?? null}
            search={search}
            page={pageNumber}
            emptyText="Новостей пока нет."
          />
        </div>
      </main>

      <RequestSection />
    </>
  );
}
