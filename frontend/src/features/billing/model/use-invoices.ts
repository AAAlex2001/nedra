"use client";

import { useEffect, useState } from "react";
import { fetchInvoices, type Invoice } from "@/entities/billing";

type InvoicesState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; items: Invoice[] };

export const useInvoices = () => {
  const [state, setState] = useState<InvoicesState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const items = await fetchInvoices();
        if (cancelled) return;

        setState({ status: "ready", items });
      } catch (error) {
        if (cancelled) return;

        const message =
          error instanceof Error && error.message ? error.message : "Не удалось загрузить счета";
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
