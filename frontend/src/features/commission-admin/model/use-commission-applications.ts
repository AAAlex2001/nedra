"use client";

import { useReducer } from "react";
import type { CommissionApplicationRecord } from "@/entities/commission";
import { deleteCommissionApplication, fetchCommissionApplications } from "../api/applications";
import { commissionAdminReducer } from "./reducer";

export const useCommissionApplications = (
  initialItems: CommissionApplicationRecord[],
  basePath: string,
) => {
  const [state, dispatch] = useReducer(commissionAdminReducer, {
    items: initialItems,
    pendingId: null,
    refreshing: false,
    error: null,
  });

  const remove = async (id: number) => {
    dispatch({ type: "delete/start", id });

    try {
      await deleteCommissionApplication(basePath, id);
      dispatch({ type: "delete/success", id });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Не удалось удалить заявку";
      dispatch({ type: "delete/error", message });
    }
  };

  const refresh = async () => {
    dispatch({ type: "refresh/start" });

    try {
      const items = await fetchCommissionApplications(basePath);
      dispatch({ type: "refresh/success", items });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Не удалось обновить список";
      dispatch({ type: "refresh/error", message });
    }
  };

  return { state, remove, refresh };
};
