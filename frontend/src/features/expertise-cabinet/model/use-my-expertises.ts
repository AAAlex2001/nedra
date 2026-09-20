"use client";

import { useEffect, useState } from "react";
import { fetchExpertCatalog, type ExpertCatalog } from "@/entities/expert";
import {
  fetchMyExpertises,
  hasPendingPayment,
  refreshExpertisePayment,
  type Expertise,
} from "@/entities/expertise";

type MyExpertisesState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; items: Expertise[]; catalog: ExpertCatalog };

const refreshPendingPayments = async (items: Expertise[]): Promise<Expertise[]> => {
  const refreshed: Expertise[] = [];

  for (const item of items) {
    if (!hasPendingPayment(item)) {
      refreshed.push(item);
      continue;
    }

    try {
      refreshed.push(await refreshExpertisePayment(item.id));
    } catch {
      refreshed.push(item);
    }
  }

  return refreshed;
};

export const useMyExpertises = () => {
  const [state, setState] = useState<MyExpertisesState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const loaded = await fetchMyExpertises();
        const catalog = await fetchExpertCatalog();
        const items = await refreshPendingPayments(loaded);
        if (cancelled) return;

        setState({ status: "ready", items, catalog });
      } catch (error) {
        if (cancelled) return;

        const message =
          error instanceof Error && error.message ? error.message : "Не удалось загрузить заявки";
        setState({ status: "error", message });
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  const replace = (updated: Expertise) => {
    if (state.status !== "ready") return;

    const items = state.items.map((item) => (item.id === updated.id ? updated : item));
    setState({ ...state, items });
  };

  return { state, replace };
};
