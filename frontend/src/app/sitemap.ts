import type { MetadataRoute } from "next";
import { PAGE_SEO, SITE_URL } from "@/shared/config/seo";

export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date();

  return Object.keys(PAGE_SEO).map((path) => ({
    url: `${SITE_URL}${path}`,
    lastModified,
    changeFrequency: path === "/" ? "weekly" : "monthly",
    priority: path === "/" ? 1 : path === "/svedeniya" ? 0.8 : 0.6,
  }));
}
