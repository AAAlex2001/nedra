import type { MetadataRoute } from "next";
import { getAllArticleSlugs } from "@/entities/article";
import { PAGE_SEO, SITE_URL } from "@/shared/config/seo";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const lastModified = new Date();

  const pages: MetadataRoute.Sitemap = Object.keys(PAGE_SEO).map((path) => ({
    url: `${SITE_URL}${path}`,
    lastModified,
    changeFrequency: path === "/" || path === "/blog" ? "weekly" : "monthly",
    priority: path === "/" ? 1 : path === "/svedeniya" || path === "/blog" ? 0.8 : 0.6,
  }));

  const articles = await getAllArticleSlugs();

  const articlePages: MetadataRoute.Sitemap = articles.map((article) => ({
    url: `${SITE_URL}/blog/${article.slug}`,
    lastModified: article.published_at ? new Date(article.published_at) : lastModified,
    changeFrequency: "monthly",
    priority: 0.7,
  }));

  return [...pages, ...articlePages];
}
