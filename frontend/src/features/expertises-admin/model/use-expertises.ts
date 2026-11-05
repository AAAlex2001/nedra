"use client";

import { useState } from "react";
import type { ServiceKind } from "@/entities/expertise";
import { deleteExpertise, fetchExpertises, updateExpertise } from "../api/expertises";
import { matchesFilter } from "./groups";
import type { ExpertiseAdminRecord, ExpertiseDraft, StatusFilter } from "./types";

const describe = (error: unknown, fallback: string): string =>
  error instanceof Error && error.message ? error.message : fallback;

export const useExpertises = (initialItems: ExpertiseAdminRecord[], basePath: string) => {
  const [items, setItems] = useState(initialItems);
  const [filter, setFilter] = useState<StatusFilter>("all");
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const visibleItems = items.filter((item) => matchesFilter(item.status, filter));

  const countFor = (value: StatusFilter): number =>
    items.filter((item) => matchesFilter(item.status, value)).length;

  const save = async (id: number, draft: ExpertiseDraft, service: ServiceKind) => {
    setPendingId(`${service}-${id}`);
    setError(null);

    try {
      const updated = await updateExpertise(basePath, id, draft, service);
      setItems(items.map((item) => (item.id === id && item.service === service ? updated : item)));
    } catch (caught) {
      setError(describe(caught, "Не удалось сохранить заявку"));
    } finally {
      setPendingId(null);
    }
  };

  const remove = async (id: number, service: ServiceKind) => {
    setPendingId(`${service}-${id}`);
    setError(null);

    try {
      await deleteExpertise(basePath, id, service);
      setItems(items.filter((item) => item.id !== id || item.service !== service));
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
