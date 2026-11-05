import { getArticles, getTags, parseArticleSort } from "@/entities/article";
import type { Metadata } from "next";
import { buildListMetadata } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import ArticlesHeading from "@/widgets/blog/articles-heading";
import ArticlesList from "@/widgets/blog/articles-list";
import RequestSection from "@/widgets/landing/request-form";
import styles from "../articles-page.module.scss";

export const dynamic = "force-dynamic";

type SearchParams = Promise<{ tag?: string; page?: string; q?: string; sort?: string }>;

export async function generateMetadata({
  searchParams,
}: {
  searchParams: SearchParams;
}): Promise<Metadata> {
  const { q } = await searchParams;

  return buildListMetadata("/novosti", q);
}

export default async function NewsPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const { tag, page, q, sort: sortParam } = await searchParams;
  const sort = parseArticleSort(sortParam);
  const pageNumber = Math.max(1, Number(page) || 1);
  const search = q?.trim() ?? "";

  const [list, tags] = await Promise.all([
    getArticles({ section: "news", tag, search, sort, page: pageNumber }),
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
            sort={sort}
            emptyText="Новостей пока нет."
          />
        </div>
      </main>

      <RequestSection />
    </>
  );
}
