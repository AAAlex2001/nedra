import { internalFetch } from "@/shared/api/server";
import type { Article, ArticleCard, ArticleList, Tag } from "../model/types";

export const ARTICLES_PER_PAGE = 12;

type ListParams = {
  tag?: string;
  page?: number;
};

const EMPTY_LIST: ArticleList = { articles: [], total: 0 };

export const getArticles = async ({ tag, page = 1 }: ListParams): Promise<ArticleList> => {
  const params = new URLSearchParams({
    limit: String(ARTICLES_PER_PAGE),
    offset: String((page - 1) * ARTICLES_PER_PAGE),
  });
  if (tag) params.set("tag", tag);

  try {
    const response = await internalFetch(`/v1/articles?${params}`, { cache: "no-store" });
    if (!response.ok) return EMPTY_LIST;

    const list: ArticleList = await response.json();

    return list;
  } catch {
    return EMPTY_LIST;
  }
};

export const getLatestArticles = async (limit: number): Promise<ArticleCard[]> => {
  try {
    const response = await internalFetch(`/v1/articles?limit=${limit}`, {
      next: { revalidate: 300 },
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

export const getTags = async (): Promise<Tag[]> => {
  try {
    const response = await internalFetch("/v1/tags", { cache: "no-store" });
    if (!response.ok) return [];

    const tags: Tag[] = await response.json();

    return tags;
  } catch {
    return [];
  }
};

export const getAllArticleSlugs = async (): Promise<ArticleCard[]> => {
  try {
    const response = await internalFetch("/v1/articles?limit=50", { cache: "no-store" });
    if (!response.ok) return [];

    const list: ArticleList = await response.json();

    return list.articles;
  } catch {
    return [];
  }
};
