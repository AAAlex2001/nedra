"use client";

import { useReducer } from "react";
import type { TagAdmin } from "@/entities/article";
import { createTag, deleteTag } from "../api/admin-articles";
import { tagsReducer } from "./reducers";

export const useTags = (basePath: string, initialItems: TagAdmin[]) => {
  const [state, dispatch] = useReducer(tagsReducer, {
    items: initialItems,
    draft: "",
    pending: false,
    error: null,
  });

  const changeDraft = (value: string) => dispatch({ type: "draft/change", value });

  const add = async () => {
    const title = state.draft.trim();
    if (title.length < 2) return;

    dispatch({ type: "request/start" });

    try {
      const tag = await createTag(basePath, title);
      dispatch({ type: "create/done", tag });
    } catch (error) {
      dispatch({
        type: "request/error",
        message: error instanceof Error ? error.message : "Не удалось создать тег",
      });
    }
  };

  const remove = async (id: number) => {
    dispatch({ type: "request/start" });

    try {
      await deleteTag(basePath, id);
      dispatch({ type: "delete/done", id });
    } catch (error) {
      dispatch({
        type: "request/error",
        message: error instanceof Error ? error.message : "Не удалось удалить тег",
      });
    }
  };

  return { state, changeDraft, add, remove };
};
