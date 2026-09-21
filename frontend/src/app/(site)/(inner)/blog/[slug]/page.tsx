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
import BlitsPromo from "@/widgets/blits-promo";
import ArticlePage from "@/widgets/blog/article-page";
import RelatedArticles from "@/widgets/blog/related-articles";
import InstituteServices from "@/widgets/landing/institute-services";
import ServicesPromo from "@/widgets/services-promo";
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
    <>
      <main className={styles.page}>
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Блог", href: "/blog" },
            { label: article.title },
          ]}
        />

        <div className={styles.body}>
          <ArticlePage
            article={article}
            promo={<BlitsPromo />}
            middle={<ServicesPromo />}
          />
        </div>
      </main>

      <InstituteServices />

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
