"use client";

import { useReducer } from "react";
import type { RequestRecord } from "@/entities/request";
import { fetchRequests } from "../api/requests";
import { requestsReducer } from "./reducer";

export const useRequests = (
  initialItems: RequestRecord[],
  basePath: string,
) => {
  const [state, dispatch] = useReducer(requestsReducer, {
    items: initialItems,
    refreshing: false,
    error: null,
  });

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

  return { state, refresh };
};
