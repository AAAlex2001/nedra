"use client";

import { useEffect, useState } from "react";
import { fetchAuditChecklist, type AuditChecklistItem } from "@/entities/expertise";

export const useAuditChecklist = () => {
  const [checklist, setChecklist] = useState<AuditChecklistItem[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const items = await fetchAuditChecklist();
        setChecklist(items);
      } catch {
        return;
      }
    };

    void load();
  }, []);

  return checklist;
};
