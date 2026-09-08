import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getArticle, getRelatedArticles } from "@/entities/article";
import { SITE_NAME, SITE_URL } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import ArticlePage from "@/widgets/blog/article-page";
import RelatedArticles from "@/widgets/blog/related-articles";
import RequestSection from "@/widgets/landing/request-form";
import styles from "../blog.module.scss";

export const dynamic = "force-dynamic";

type Params = Promise<{ slug: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { slug } = await params;
  const article = await getArticle(slug);

  if (!article) {
    return { title: "Статья не найдена", robots: { index: false } };
  }

  const url = `${SITE_URL}/blog/${article.slug}`;
  const description = article.seo_description ?? article.description ?? undefined;
  const keywords = article.seo_keywords
    ? article.seo_keywords.split(",").map((word) => word.trim()).filter(Boolean)
    : undefined;

  return {
    title: article.seo_title ?? article.title,
    description,
    keywords,
    alternates: { canonical: url },
    openGraph: {
      type: "article",
      url,
      siteName: SITE_NAME,
      locale: "ru_RU",
      title: article.title,
      description,
      publishedTime: article.published_at ?? undefined,
      images: article.cover_image ? [{ url: article.cover_image }] : undefined,
    },
    twitter: {
      card: article.cover_image ? "summary_large_image" : "summary",
      title: article.title,
      description,
      images: article.cover_image ? [article.cover_image] : undefined,
    },
  };
}

export default async function ArticleRoute({ params }: { params: Params }) {
  const { slug } = await params;
  const article = await getArticle(slug);

  if (!article) notFound();

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

      <RequestSection />
    </main>
  );
}
