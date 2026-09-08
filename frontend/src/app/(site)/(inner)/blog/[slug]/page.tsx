import type { Metadata } from "next";
import { notFound, permanentRedirect } from "next/navigation";
import {
  NOT_FOUND_METADATA,
  articlePath,
  buildArticleMetadata,
  getArticle,
  getRelatedArticles,
} from "@/entities/article";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import ArticlePage from "@/widgets/blog/article-page";
import RelatedArticles from "@/widgets/blog/related-articles";
import styles from "../../../articles-page.module.scss";

export const dynamic = "force-dynamic";

type Params = Promise<{ slug: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { slug } = await params;
  const article = await getArticle(slug);

  if (!article) return NOT_FOUND_METADATA;

  return buildArticleMetadata(article);
}

export default async function BlogArticleRoute({ params }: { params: Params }) {
  const { slug } = await params;
  const article = await getArticle(slug);

  if (!article) notFound();
  if (article.section !== "blog") permanentRedirect(articlePath(article));

  const related = await getRelatedArticles(slug, 10);

  return (
    <main className={styles.page}>
      <Breadcrumbs
        items={[
          { label: "Главная", href: "/" },
          { label: "Блог", href: "/blog" },
          { label: article.title },
        ]}
      />

      <div className={styles.body}>
        <ArticlePage article={article} />
        {related.length > 0 && <RelatedArticles articles={related} />}
      </div>
    </main>
  );
}
