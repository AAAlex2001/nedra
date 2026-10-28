import { getArticles, getTags } from "@/entities/article";
import type { Metadata } from "next";
import { buildListMetadata } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import ArticlesHeading from "@/widgets/blog/articles-heading";
import ArticlesList from "@/widgets/blog/articles-list";
import styles from "../../articles-page.module.scss";

export const dynamic = "force-dynamic";

type SearchParams = Promise<{ tag?: string; page?: string; q?: string }>;

export async function generateMetadata({
  searchParams,
}: {
  searchParams: SearchParams;
}): Promise<Metadata> {
  const { q } = await searchParams;

  return buildListMetadata("/blog", q);
}

export default async function BlogPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const { tag, page, q } = await searchParams;
  const pageNumber = Math.max(1, Number(page) || 1);
  const search = q?.trim() ?? "";

  const [list, tags] = await Promise.all([
    getArticles({ section: "blog", tag, search, page: pageNumber }),
    getTags("blog"),
  ]);

  return (
    <main className={styles.page}>
      <Breadcrumbs items={[{ label: "Главная", href: "/" }, { label: "Блог" }]} />

      <div className={styles.body}>
        <ArticlesHeading
          title="Блог"
          subtitle="Законодательство, промышленная безопасность, проектирование и экспертиза — разбираем изменения и делимся практикой"
          total={list.total}
        />

        <ArticlesList
          section="blog"
          list={list}
          tags={tags}
          activeTag={tag ?? null}
          search={search}
          page={pageNumber}
          emptyText="Статей пока нет."
        />
      </div>
    </main>
  );
}
