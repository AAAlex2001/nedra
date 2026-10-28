import { API_URL, readErrorMessage } from "@/shared/api";
import type { ArticleSection, ArticleSuggestion } from "../model/types";

export const fetchSuggestions = async (
  section: ArticleSection,
  search: string,
  signal: AbortSignal,
): Promise<ArticleSuggestion[]> => {
  const params = new URLSearchParams({ section, q: search });

  const response = await fetch(`${API_URL}/v1/articles/suggest?${params}`, { signal });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const items: ArticleSuggestion[] = await response.json();

  return items;
};
