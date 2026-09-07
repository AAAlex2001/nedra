"use client";

import { useReducer } from "react";
import type { RequestRecord } from "@/entities/request";
import { deleteRequest, fetchRequests } from "../api/requests";
import { requestsReducer } from "./reducer";

export const useRequests = (
  initialItems: RequestRecord[],
  basePath: string,
) => {
  const [state, dispatch] = useReducer(requestsReducer, {
    items: initialItems,
    pendingId: null,
    refreshing: false,
    error: null,
  });

  const remove = async (id: number) => {
    dispatch({ type: "delete/start", id });

    try {
      await deleteRequest(basePath, id);
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
      const items = await fetchRequests(basePath);
      dispatch({ type: "refresh/success", items });
    } catch (error) {
      dispatch({
        type: "refresh/error",
        message:
          error instanceof Error ? error.message : "Не удалось обновить список",
      });
    }
  };

  return { state, remove, refresh };
};
