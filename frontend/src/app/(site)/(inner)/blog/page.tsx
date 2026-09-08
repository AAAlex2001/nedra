import { getArticles, getTags } from "@/entities/article";
import { buildMetadata } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import ArticlesList from "@/widgets/blog/articles-list";
import styles from "./blog.module.scss";

export const dynamic = "force-dynamic";

export const metadata = buildMetadata("/blog");

type SearchParams = Promise<{ tag?: string; page?: string }>;

export default async function BlogPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const { tag, page } = await searchParams;
  const pageNumber = Math.max(1, Number(page) || 1);

  const [list, tags] = await Promise.all([
    getArticles({ tag, page: pageNumber }),
    getTags(),
  ]);

  return (
    <main className={styles.page}>
      <Breadcrumbs items={[{ label: "Главная", href: "/" }, { label: "Блог" }]} />

      <div className={styles.body}>
        <div className={styles.heading}>
          <h1 className={styles.title}>Блог</h1>
          <p className={styles.subtitle}>
            Законодательство, промышленная безопасность, проектирование и экспертиза —
            разбираем изменения и делимся практикой
          </p>
        </div>

        <ArticlesList list={list} tags={tags} activeTag={tag ?? null} page={pageNumber} />
      </div>
    </main>
  );
}
