"use client";

import { useEffect, useState } from "react";
import { fetchAuditors, type AuditTeamMember } from "@/entities/expertise";

const LOAD_FAILED = "Не удалось загрузить список аудиторов";

export const useAuditors = () => {
  const [auditors, setAuditors] = useState<AuditTeamMember[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const items = await fetchAuditors();
        setAuditors(items);
      } catch (caught) {
        setError(caught instanceof Error && caught.message ? caught.message : LOAD_FAILED);
      }
    };

    void load();
  }, []);

  return { auditors, error };
};
