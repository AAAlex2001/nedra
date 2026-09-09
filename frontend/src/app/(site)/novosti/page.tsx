import { getArticles, getTags } from "@/entities/article";
import { buildMetadata } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import ArticlesList from "@/widgets/blog/articles-list";
import RequestSection from "@/widgets/landing/request-form";
import styles from "../articles-page.module.scss";

export const dynamic = "force-dynamic";

export const metadata = buildMetadata("/novosti");

type SearchParams = Promise<{ tag?: string; page?: string }>;

export default async function NewsPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const { tag, page } = await searchParams;
  const pageNumber = Math.max(1, Number(page) || 1);

  const [list, tags] = await Promise.all([
    getArticles({ section: "news", tag, page: pageNumber }),
    getTags("news"),
  ]);

  return (
    <>
      <main className={styles.page}>
        <Breadcrumbs items={[{ label: "Главная", href: "/" }, { label: "Новости" }]} />

        <div className={styles.body}>
          <div className={styles.heading}>
            <h1 className={styles.title}>Новости</h1>
            <p className={styles.subtitle}>
              Изменения законодательства, новые требования Ростехнадзора, практика
              проектирования, экспертизы и экологии — коротко и по делу
            </p>
          </div>

          <ArticlesList
            basePath="/novosti"
            list={list}
            tags={tags}
            activeTag={tag ?? null}
            page={pageNumber}
            emptyText="Новостей пока нет."
          />
        </div>
      </main>

      <RequestSection />
    </>
  );
}
