"use client";

import { useReducer } from "react";
import type { ArticleAdminCard } from "@/entities/article";
import { deleteArticle } from "../api/admin-articles";
import { listReducer } from "./reducers";

export const useArticlesList = (basePath: string, initialItems: ArticleAdminCard[]) => {
  const [state, dispatch] = useReducer(listReducer, {
    items: initialItems,
    pendingId: null,
    error: null,
  });

  const remove = async (id: number) => {
    dispatch({ type: "delete/start", id });

    try {
      await deleteArticle(basePath, id);
      dispatch({ type: "delete/done", id });
    } catch (error) {
      dispatch({
        type: "delete/error",
        message: error instanceof Error ? error.message : "Не удалось удалить статью",
      });
    }
  };

  return { state, remove };
};
