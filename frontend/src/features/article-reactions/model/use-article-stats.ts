"use client";

import { useEffect, useReducer } from "react";
import type { ArticleStats } from "@/entities/article";
import { registerView, removeReaction, setReaction } from "../api/reactions";

type State = {
  stats: ArticleStats;
  pending: boolean;
  error: string | null;
};

type Action =
  | { type: "stats/loaded"; stats: ArticleStats }
  | { type: "reaction/start" }
  | { type: "reaction/error"; message: string };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "stats/loaded":
      return { stats: action.stats, pending: false, error: null };

    case "reaction/start":
      return { ...state, pending: true, error: null };

    case "reaction/error":
      return { ...state, pending: false, error: action.message };

    default:
      return state;
  }
};

export const useArticleStats = (slug: string, initial: ArticleStats) => {
  const [state, dispatch] = useReducer(reducer, {
    stats: initial,
    pending: false,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;

    const loadStats = async () => {
      try {
        const stats = await registerView(slug);
        if (!cancelled) dispatch({ type: "stats/loaded", stats });
      } catch {
        return;
      }
    };

    void loadStats();

    return () => {
      cancelled = true;
    };
  }, [slug]);

  const react = async (value: 1 | -1) => {
    dispatch({ type: "reaction/start" });

    try {
      const stats =
        state.stats.my_reaction === value
          ? await removeReaction(slug)
          : await setReaction(slug, value);

      dispatch({ type: "stats/loaded", stats });
    } catch (error) {
      dispatch({
        type: "reaction/error",
        message: error instanceof Error ? error.message : "Не удалось сохранить реакцию",
      });
    }
  };

  return { ...state, react };
};
