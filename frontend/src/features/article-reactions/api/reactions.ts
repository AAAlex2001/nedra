import type { ArticleStats } from "@/entities/article";
import { API_URL, readErrorMessage } from "@/shared/api";

const articleUrl = (slug: string) => `${API_URL}/v1/articles/${encodeURIComponent(slug)}`;

const requestStats = async (url: string, init?: RequestInit): Promise<ArticleStats> => {
  const response = await fetch(url, init);

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const stats: ArticleStats = await response.json();

  return stats;
};

export const registerView = (slug: string) =>
  requestStats(`${articleUrl(slug)}/view`, { method: "POST" });

export const setReaction = (slug: string, value: 1 | -1) =>
  requestStats(`${articleUrl(slug)}/reaction`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value }),
  });

export const removeReaction = (slug: string) =>
  requestStats(`${articleUrl(slug)}/reaction`, { method: "DELETE" });
