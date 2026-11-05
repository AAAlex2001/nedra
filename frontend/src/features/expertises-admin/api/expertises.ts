import type { ServiceKind } from "@/entities/expertise";
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
  service: ServiceKind,
): Promise<ExpertiseAdminRecord> => {
  const common = {
    service,
    status: draft.status,
    price: draft.price === "" ? null : draft.price,

  };

  const executorId = draft.expertId === "" ? null : Number(draft.expertId);
  const body = service === "audit"
    ? { ...common, lead_id: executorId }
    : { ...common, expert_id: executorId, contract_kind: draft.contractKind || null };

  const response = await fetch(`${basePath}/api/expertises/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const items = await fetchExpertises(basePath);
  const updated = items.find((item) => item.id === id && item.service === service);

  if (!updated) throw new Error("Заявка не найдена после сохранения");

  return updated;
};

export const deleteExpertise = async (basePath: string, id: number, service: ServiceKind): Promise<void> => {
  const response = await fetch(`${basePath}/api/expertises/${id}?service=${service}`, { method: "DELETE" });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }
};
