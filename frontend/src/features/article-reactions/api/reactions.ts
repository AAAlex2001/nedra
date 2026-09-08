import type { ArticleStats } from "@/entities/article";
import { API_URL, readErrorMessage } from "@/shared/api";

const articleUrl = (slug: string) => `${API_URL}/v1/articles/${encodeURIComponent(slug)}`;

const parseStats = async (response: Response): Promise<ArticleStats> => {
  if (!response.ok) throw new Error(await readErrorMessage(response));

  return (await response.json()) as ArticleStats;
};

export const registerView = (slug: string) =>
  fetch(`${articleUrl(slug)}/view`, { method: "POST" }).then(parseStats);

export const setReaction = (slug: string, value: 1 | -1) =>
  fetch(`${articleUrl(slug)}/reaction`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value }),
  }).then(parseStats);

export const removeReaction = (slug: string) =>
  fetch(`${articleUrl(slug)}/reaction`, { method: "DELETE" }).then(parseStats);
