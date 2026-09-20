"use client";

import { useEffect, useState } from "react";
import { fetchCompany, saveCompany, type Company, type CompanyDraft } from "@/entities/billing";

type CompanyState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; company: Company | null };

const describe = (error: unknown, fallback: string): string =>
  error instanceof Error && error.message ? error.message : fallback;

export const useCompany = () => {
  const [state, setState] = useState<CompanyState>({ status: "loading" });
  const [pending, setPending] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const company = await fetchCompany();
        if (cancelled) return;

        setState({ status: "ready", company });
      } catch (error) {
        if (cancelled) return;

        setState({ status: "error", message: describe(error, "Не удалось загрузить реквизиты") });
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  const save = async (draft: CompanyDraft) => {
    setPending(true);
    setSaveError(null);

    try {
      const company = await saveCompany(draft);
      setState({ status: "ready", company });
    } catch (error) {
      setSaveError(describe(error, "Не удалось сохранить реквизиты"));
    } finally {
      setPending(false);
    }
  };

  return { state, pending, saveError, save };
};
