"use client";

import { useReducer } from "react";
import type { RequestRecord } from "@/entities/request";
import { deleteRequest, fetchRequests } from "../api/requests";
import { requestsReducer } from "./reducer";

export const useRequests = (initialItems: RequestRecord[]) => {
  const [state, dispatch] = useReducer(requestsReducer, {
    items: initialItems,
    pendingId: null,
    refreshing: false,
    error: null,
  });

  const remove = async (id: number) => {
    dispatch({ type: "delete/start", id });

    try {
      await deleteRequest(id);
      dispatch({ type: "delete/success", id });
    } catch (error) {
      dispatch({
        type: "delete/error",
        message:
          error instanceof Error ? error.message : "Не удалось удалить заявку",
      });
    }
  };

  const refresh = async () => {
    dispatch({ type: "refresh/start" });

    try {
      dispatch({ type: "refresh/success", items: await fetchRequests() });
    } catch (error) {
      dispatch({
        type: "refresh/error",
        message:
          error instanceof Error ? error.message : "Не удалось обновить список",
      });
    }
  };

  const clearError = () => dispatch({ type: "error/clear" });

  return { state, remove, refresh, clearError };
};
