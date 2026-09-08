import type { Metadata } from "next";
import { SITE_NAME, SITE_URL } from "@/shared/config/seo";
import type { Article } from "../model/types";
import { articlePath } from "./paths";

export const NOT_FOUND_METADATA: Metadata = {
  title: "Статья не найдена",
  robots: { index: false },
};

export const buildArticleMetadata = (article: Article): Metadata => {
  const url = `${SITE_URL}${articlePath(article)}`;
  const description = article.seo_description ?? article.description ?? undefined;

  let keywords: string[] | undefined;
  if (article.seo_keywords) {
    keywords = article.seo_keywords
      .split(",")
      .map((word) => word.trim())
      .filter(Boolean);
  }

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
};
