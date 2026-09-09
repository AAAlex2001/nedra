import { internalFetch } from "@/shared/api/server";
import type { Article, ArticleCard, ArticleList, ArticleSection, Tag } from "../model/types";

export const ARTICLES_PER_PAGE = 12;
const MAX_PAGE_SIZE = 50;

type ListParams = {
  section: ArticleSection;
  tag?: string;
  page?: number;
};

const EMPTY_LIST: ArticleList = { articles: [], total: 0 };

export const getArticles = async ({ section, tag, page = 1 }: ListParams): Promise<ArticleList> => {
  const wanted = page * ARTICLES_PER_PAGE;
  const articles: ArticleCard[] = [];
  let total = 0;

  try {
    while (articles.length < wanted) {
      const params = new URLSearchParams({
        section,
        limit: String(Math.min(MAX_PAGE_SIZE, wanted - articles.length)),
        offset: String(articles.length),
      });
      if (tag) params.set("tag", tag);

      const response = await internalFetch(`/v1/articles?${params}`, { cache: "no-store" });
      if (!response.ok) return EMPTY_LIST;

      const chunk: ArticleList = await response.json();
      articles.push(...chunk.articles);
      total = chunk.total;

      if (chunk.articles.length === 0 || articles.length >= total) break;
    }
  } catch {
    return EMPTY_LIST;
  }

  return { articles, total };
};

export const getLatestArticles = async (
  section: ArticleSection,
  limit: number,
): Promise<ArticleCard[]> => {
  try {
    const response = await internalFetch(`/v1/articles?section=${section}&limit=${limit}`, {
      cache: "no-store",
    });
    if (!response.ok) return [];

    const list: ArticleList = await response.json();

    return list.articles;
  } catch {
    return [];
  }
};

export const getArticle = async (slug: string): Promise<Article | null> => {
  try {
    const response = await internalFetch(`/v1/articles/${encodeURIComponent(slug)}`, {
      cache: "no-store",
    });
    if (!response.ok) return null;

    const article: Article = await response.json();

    return article;
  } catch {
    return null;
  }
};

export const getRelatedArticles = async (slug: string, limit = 10): Promise<ArticleCard[]> => {
  try {
    const response = await internalFetch(
      `/v1/articles/${encodeURIComponent(slug)}/related?limit=${limit}`,
      { cache: "no-store" },
    );
    if (!response.ok) return [];

    const articles: ArticleCard[] = await response.json();

    return articles;
  } catch {
    return [];
  }
};

export const getTags = async (section: ArticleSection): Promise<Tag[]> => {
  try {
    const response = await internalFetch(`/v1/tags?section=${section}`, { cache: "no-store" });
    if (!response.ok) return [];

    const tags: Tag[] = await response.json();

    return tags;
  } catch {
    return [];
  }
};

export const getAllArticleCards = async (): Promise<ArticleCard[]> => {
  const cards: ArticleCard[] = [];
  let offset = 0;

  try {
    while (true) {
      const response = await internalFetch(
        `/v1/articles?limit=${MAX_PAGE_SIZE}&offset=${offset}`,
        { cache: "no-store" },
      );
      if (!response.ok) break;

      const list: ArticleList = await response.json();
      cards.push(...list.articles);
      offset += MAX_PAGE_SIZE;

      if (list.articles.length === 0 || cards.length >= list.total) break;
    }
  } catch {
    return cards;
  }

  return cards;
};
