"use client";

import { useEffect, useState } from "react";
import { fetchExpertCatalog, type Certificate, type ExpertCatalog } from "@/entities/expert";
import { fetchIncomingExpertises, type Expertise } from "@/entities/expertise";

const POLL_INTERVAL = 60_000;

type IncomingState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; items: Expertise[]; catalog: ExpertCatalog };

const unique = (values: string[]): string[] =>
  values.filter((value, index) => values.indexOf(value) === index);

export const useIncomingExpertises = (certificates: Certificate[]) => {
  const [objectCode, setObjectCode] = useState("");
  const [areaCode, setAreaCode] = useState("");
  const [state, setState] = useState<IncomingState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const items = await fetchIncomingExpertises("", "");
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
    const timer = window.setInterval(() => void load(), POLL_INTERVAL);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  const objectCodes = unique(certificates.map((item) => item.object_code));
  const areaCodes = unique(certificates.map((item) => item.area_code));

  const items = state.status === "ready" ? state.items : [];

  const matchesObject = (item: Expertise) =>
    objectCode === "" || item.object_code === null || item.object_code === objectCode;

  const matchesArea = (item: Expertise) =>
    areaCode === "" || item.area_code === null || item.area_code === areaCode;

  const visibleItems = items.filter((item) => matchesObject(item) && matchesArea(item));

  const replace = (updated: Expertise) => {
    if (state.status !== "ready") return;

    const next = state.items
      .map((item) => (item.id === updated.id ? updated : item))
      .filter((item) => item.status === "new");
    setState({ ...state, items: next });
  };

  return {
    state,
    visibleItems,
    objectCodes,
    areaCodes,
    objectCode,
    areaCode,
    setObjectCode,
    setAreaCode,
    replace,
  };
};
