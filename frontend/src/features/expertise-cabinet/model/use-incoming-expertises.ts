"use client";

import { useEffect, useState } from "react";
import { fetchExpertCatalog, type ExpertCatalog } from "@/entities/expert";
import { fetchIncomingExpertises, type Expertise } from "@/entities/expertise";

type IncomingState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; items: Expertise[]; catalog: ExpertCatalog };

export const useIncomingExpertises = () => {
  const [objectCode, setObjectCode] = useState("");
  const [areaCode, setAreaCode] = useState("");
  const [state, setState] = useState<IncomingState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const items = await fetchIncomingExpertises(objectCode, areaCode);
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
  }, [objectCode, areaCode]);

  const replace = (updated: Expertise) => {
    if (state.status !== "ready") return;

    const items = state.items
      .map((item) => (item.id === updated.id ? updated : item))
      .filter((item) => item.status === "new");
    setState({ ...state, items });
  };

  return { state, objectCode, areaCode, setObjectCode, setAreaCode, replace };
};
