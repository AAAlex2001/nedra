"use client";

import { useReducer } from "react";
import type { ExpertApplicationRecord } from "@/entities/expert";
import {
  approveApplication,
  deleteExpert,
  fetchApplications,
  rejectApplication,
} from "../api/applications";
import { applicationsReducer } from "./reducer";
import type { StatusFilter } from "./types";

const describe = (error: unknown, fallback: string): string =>
  error instanceof Error && error.message ? error.message : fallback;

export const useApplications = (initialItems: ExpertApplicationRecord[], basePath: string) => {
  const [state, dispatch] = useReducer(applicationsReducer, {
    items: initialItems,
    filter: "pending",
    pendingId: null,
    refreshing: false,
    error: null,
  });

  const visibleItems =
    state.filter === "all"
      ? state.items
      : state.items.filter((item) => item.status === state.filter);

  const setFilter = (filter: StatusFilter) => dispatch({ type: "filter/set", filter });

  const approve = async (id: number) => {
    dispatch({ type: "review/start", id });

    try {
      const item = await approveApplication(basePath, id);
      dispatch({ type: "review/success", item });
    } catch (error) {
      dispatch({ type: "review/error", message: describe(error, "Не удалось одобрить заявку") });
    }
  };

  const reject = async (id: number, comment: string) => {
    dispatch({ type: "review/start", id });

    try {
      const item = await rejectApplication(basePath, id, comment);
      dispatch({ type: "review/success", item });
    } catch (error) {
      dispatch({ type: "review/error", message: describe(error, "Не удалось отклонить заявку") });
    }
  };

  const removeExpert = async (application: ExpertApplicationRecord) => {
    if (application.user_id === null) return;

    dispatch({ type: "review/start", id: application.id });

    try {
      await deleteExpert(basePath, application.user_id);
      const items = await fetchApplications(basePath);
      dispatch({ type: "refresh/success", items });
      dispatch({ type: "review/done" });
    } catch (error) {
      dispatch({ type: "review/error", message: describe(error, "Не удалось удалить эксперта") });
    }
  };

  const refresh = async () => {
    dispatch({ type: "refresh/start" });

    try {
      const items = await fetchApplications(basePath);
      dispatch({ type: "refresh/success", items });
    } catch (error) {
      dispatch({ type: "refresh/error", message: describe(error, "Не удалось обновить список") });
    }
  };

  return { state, visibleItems, setFilter, approve, reject, removeExpert, refresh };
};
