"use client";

import { useReducer } from "react";
import type { RequestRecord } from "@/entities/request";
import { fetchRequests } from "../api/requests";
import { requestsReducer } from "./reducer";

export const useRequests = (initialItems: RequestRecord[]) => {
  const [state, dispatch] = useReducer(requestsReducer, {
    items: initialItems,
    refreshing: false,
    error: null,
  });

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

  return { state, refresh };
};
