import type { ArticleSection } from "../model/types";

export const SECTION_PATH: Record<ArticleSection, string> = {
  blog: "/blog",
  news: "/novosti",
};

export const SECTION_TITLE: Record<ArticleSection, string> = {
  blog: "Блог",
  news: "Новости",
};

type Addressable = {
  section: ArticleSection;
  slug: string;
};

export const articlePath = (article: Addressable) =>
  `${SECTION_PATH[article.section]}/${article.slug}`;
