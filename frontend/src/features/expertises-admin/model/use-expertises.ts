"use client";

import { useState } from "react";
import type { ExpertiseStatus } from "@/entities/expertise";
import { deleteExpertise, fetchExpertises, updateExpertise } from "../api/expertises";
import { matchesFilter } from "./groups";
import type { ExpertiseAdminRecord, StatusFilter } from "./types";

const describe = (error: unknown, fallback: string): string =>
  error instanceof Error && error.message ? error.message : fallback;

export const useExpertises = (initialItems: ExpertiseAdminRecord[], basePath: string) => {
  const [items, setItems] = useState(initialItems);
  const [filter, setFilter] = useState<StatusFilter>("all");
  const [pendingId, setPendingId] = useState<number | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const visibleItems = items.filter((item) => matchesFilter(item.status, filter));

  const countFor = (value: StatusFilter): number =>
    items.filter((item) => matchesFilter(item.status, value)).length;

  const save = async (id: number, status: ExpertiseStatus, price: string | null) => {
    setPendingId(id);
    setError(null);

    try {
      const updated = await updateExpertise(basePath, id, status, price);
      setItems(items.map((item) => (item.id === id ? updated : item)));
    } catch (caught) {
      setError(describe(caught, "Не удалось сохранить заявку"));
    } finally {
      setPendingId(null);
    }
  };

  const remove = async (id: number) => {
    setPendingId(id);
    setError(null);

    try {
      await deleteExpertise(basePath, id);
      setItems(items.filter((item) => item.id !== id));
    } catch (caught) {
      setError(describe(caught, "Не удалось удалить заявку"));
    } finally {
      setPendingId(null);
    }
  };

  const refresh = async () => {
    setRefreshing(true);
    setError(null);

    try {
      setItems(await fetchExpertises(basePath));
    } catch (caught) {
      setError(describe(caught, "Не удалось обновить список"));
    } finally {
      setRefreshing(false);
    }
  };

  return {
    visibleItems,
    filter,
    pendingId,
    refreshing,
    error,
    countFor,
    setFilter,
    save,
    remove,
    refresh,
  };
};
