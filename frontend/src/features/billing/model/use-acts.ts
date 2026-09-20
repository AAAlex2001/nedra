"use client";

import { useEffect, useState } from "react";
import { fetchActs, type Act } from "@/entities/billing";

type ActsState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; items: Act[] };

export const useActs = () => {
  const [state, setState] = useState<ActsState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const items = await fetchActs();
        if (cancelled) return;

        setState({ status: "ready", items });
      } catch (error) {
        if (cancelled) return;

        const message =
          error instanceof Error && error.message ? error.message : "Не удалось загрузить акты";
        setState({ status: "error", message });
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  return state;
};
