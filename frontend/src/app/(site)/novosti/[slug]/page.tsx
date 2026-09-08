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
import InstituteServices from "@/widgets/landing/institute-services";
import RequestSection from "@/widgets/landing/request-form";
import styles from "../../articles-page.module.scss";

export const dynamic = "force-dynamic";

type Params = Promise<{ slug: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { slug } = await params;
  const article = await getArticle(slug);

  if (!article) return NOT_FOUND_METADATA;

  return buildArticleMetadata(article);
}

export default async function NewsArticleRoute({ params }: { params: Params }) {
  const { slug } = await params;
  const article = await getArticle(slug);

  if (!article) notFound();
  if (article.section !== "news") permanentRedirect(articlePath(article));

  const related = await getRelatedArticles(slug, 10);

  return (
    <>
      <main className={styles.page}>
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Новости", href: "/novosti" },
            { label: article.title },
          ]}
        />

        <div className={styles.body}>
          <ArticlePage article={article} middle={<InstituteServices />} />
        </div>
      </main>

      <RequestSection />

      {related.length > 0 && (
        <div className={styles.page}>
          <div className={styles.body}>
            <RelatedArticles articles={related} />
          </div>
        </div>
      )}
    </>
  );
}
