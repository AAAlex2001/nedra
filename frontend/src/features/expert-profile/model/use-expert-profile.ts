"use client";

import { useEffect, useState } from "react";
import { fetchExpertCatalog, fetchExpertProfile, type ExpertCatalog, type ExpertProfile } from "@/entities/expert";

type ProfileState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; profile: ExpertProfile; catalog: ExpertCatalog };

export const useExpertProfile = () => {
  const [state, setState] = useState<ProfileState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const profile = await fetchExpertProfile();
        const catalog = await fetchExpertCatalog();
        if (cancelled) return;

        setState({ status: "ready", profile, catalog });
      } catch (error) {
        if (cancelled) return;

        const message =
          error instanceof Error && error.message
            ? error.message
            : "Не удалось загрузить профиль эксперта";
        setState({ status: "error", message });
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  const replaceProfile = (profile: ExpertProfile) => {
    if (state.status !== "ready") return;

    setState({ ...state, profile });
  };

  return { state, replaceProfile };
};
