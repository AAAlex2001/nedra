"use client";

import { useReducer } from "react";
import type { ArticleAdminList } from "@/entities/article";
import { deleteArticle, fetchArticles } from "../api/admin-articles";
import type { AdminListFilters } from "../lib/list-href";
import { listReducer } from "./reducers";

const errorText = (error: unknown, fallback: string): string =>
  error instanceof Error ? error.message : fallback;

export const useArticlesList = (
  basePath: string,
  initialList: ArticleAdminList,
  filters: AdminListFilters,
) => {
  const [state, dispatch] = useReducer(listReducer, {
    items: initialList.articles,
    total: initialList.total,
    pendingId: null,
    loadingMore: false,
    error: null,
  });

  const hasMore = state.items.length < state.total;

  const remove = async (id: number) => {
    dispatch({ type: "delete/start", id });

    try {
      await deleteArticle(basePath, id);
      dispatch({ type: "delete/done", id });
    } catch (error) {
      dispatch({ type: "delete/error", message: errorText(error, "Не удалось удалить статью") });
    }
  };

  const loadMore = async () => {
    dispatch({ type: "more/start" });

    try {
      const page = await fetchArticles(basePath, filters, state.items.length);
      dispatch({ type: "more/done", items: page.articles, total: page.total });
    } catch (error) {
      dispatch({ type: "more/error", message: errorText(error, "Не удалось загрузить статьи") });
    }
  };

  return { state, hasMore, remove, loadMore };
};
