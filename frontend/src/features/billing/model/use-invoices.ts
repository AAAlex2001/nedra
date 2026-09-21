"use client";

import { useEffect, useState } from "react";
import { fetchInvoices, reportInvoicePaid, type Invoice } from "@/entities/billing";

type InvoicesState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; items: Invoice[] };

export const useInvoices = () => {
  const [state, setState] = useState<InvoicesState>({ status: "loading" });
  const [pendingId, setPendingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const items = await fetchInvoices();
        if (cancelled) return;

        setState({ status: "ready", items });
      } catch (caught) {
        if (cancelled) return;

        const message =
          caught instanceof Error && caught.message ? caught.message : "Не удалось загрузить счета";
        setState({ status: "error", message });
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  const report = async (id: number) => {
    if (state.status !== "ready") return;

    setPendingId(id);
    setError(null);

    try {
      const updated = await reportInvoicePaid(id);
      const items = state.items.map((item) => (item.id === id ? updated : item));
      setState({ status: "ready", items });
    } catch (caught) {
      const message =
        caught instanceof Error && caught.message
          ? caught.message
          : "Не удалось сообщить об оплате";
      setError(message);
    } finally {
      setPendingId(null);
    }
  };

  return { state, pendingId, error, report };
};
