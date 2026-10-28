"use client";

import { useEffect, useState } from "react";
import { fetchSuggestions, type ArticleSection, type ArticleSuggestion } from "@/entities/article";

const MIN_LENGTH = 2;
const DEBOUNCE_MS = 250;

export const useSuggestions = (section: ArticleSection, query: string): ArticleSuggestion[] => {
  const [items, setItems] = useState<ArticleSuggestion[]>([]);

  const search = query.trim();
  const enabled = search.length >= MIN_LENGTH;

  useEffect(() => {
    if (!enabled) return;

    const controller = new AbortController();

    const loadSuggestions = async () => {
      try {
        const found = await fetchSuggestions(section, search, controller.signal);
        setItems(found);
      } catch {
        return;
      }
    };

    const timer = window.setTimeout(loadSuggestions, DEBOUNCE_MS);

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [section, search, enabled]);

  return enabled ? items : [];
};
