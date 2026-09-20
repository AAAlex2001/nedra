"use client";

import { useEffect, useState } from "react";
import { fetchExpertCatalog, type ExpertCatalog } from "@/entities/expert";
import { fetchAssignedExpertises, type Expertise } from "@/entities/expertise";

type AssignedState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; items: Expertise[]; catalog: ExpertCatalog };

export const useAssignedExpertises = () => {
  const [state, setState] = useState<AssignedState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const items = await fetchAssignedExpertises();
        const catalog = await fetchExpertCatalog();
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
