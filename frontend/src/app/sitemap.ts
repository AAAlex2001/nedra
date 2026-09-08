import type { MetadataRoute } from "next";
import { articlePath, getAllArticleCards } from "@/entities/article";
import { PAGE_SEO, SITE_URL } from "@/shared/config/seo";

const WEEKLY_PATHS = new Set(["/", "/blog", "/novosti"]);
const IMPORTANT_PATHS = new Set(["/svedeniya", "/blog", "/novosti"]);

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const lastModified = new Date();

  const pages: MetadataRoute.Sitemap = Object.keys(PAGE_SEO).map((path) => {
    let priority = 0.6;
    if (path === "/") priority = 1;
    else if (IMPORTANT_PATHS.has(path)) priority = 0.8;

    return {
      url: `${SITE_URL}${path}`,
      lastModified,
      changeFrequency: WEEKLY_PATHS.has(path) ? "weekly" : "monthly",
      priority,
    };
  });

  const articles = await getAllArticleCards();

  const articlePages: MetadataRoute.Sitemap = articles.map((article) => ({
    url: `${SITE_URL}${articlePath(article)}`,
    lastModified: article.published_at ? new Date(article.published_at) : lastModified,
    changeFrequency: "monthly",
    priority: 0.7,
  }));

  return [...pages, ...articlePages];
}
