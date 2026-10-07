import { readErrorMessage } from "@/shared/api";
import type { ExpertiseAdminRecord, ExpertiseDraft } from "../model/types";

export const fetchExpertises = async (basePath: string): Promise<ExpertiseAdminRecord[]> => {
  const response = await fetch(`${basePath}/api/expertises`, { cache: "no-store" });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const items: ExpertiseAdminRecord[] = await response.json();

  return items;
};

export const updateExpertise = async (
  basePath: string,
  id: number,
  draft: ExpertiseDraft,
): Promise<ExpertiseAdminRecord> => {
  const body = {
    status: draft.status,
    price: draft.price === "" ? null : draft.price,
    expert_id: draft.expertId === "" ? null : Number(draft.expertId),
    contract_kind: draft.contractKind === "" ? null : draft.contractKind,
  };

  const response = await fetch(`${basePath}/api/expertises/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const updated: ExpertiseAdminRecord = await response.json();

  return updated;
};

export const deleteExpertise = async (basePath: string, id: number): Promise<void> => {
  const response = await fetch(`${basePath}/api/expertises/${id}`, { method: "DELETE" });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }
};
