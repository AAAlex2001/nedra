import type { WorkSummaryResponse } from "../model/api-responses";
import type { Expertise } from "../model/types";
import { fetchAudit } from "./read-audit";
import { fetchExpertise } from "./read-expertise";
import { requestJson } from "./request";

const fetchWorkList = async (scope: "my" | "incoming" | "assigned"): Promise<Expertise[]> => {
  const [expertises, audits] = await Promise.all([
    requestJson<WorkSummaryResponse[]>(`/expertises/${scope}`),
    requestJson<WorkSummaryResponse[]>(`/audit/${scope}`),
  ]);
  const cards = await Promise.all([
    ...expertises.map((item) => fetchExpertise(item.id)),
    ...audits.map((item) => fetchAudit(item.id)),
  ]);

  return cards.sort((first, second) =>
    second.created_at.localeCompare(first.created_at) || second.id - first.id,
  );
};

export const fetchMyExpertises = () => fetchWorkList("my");
export const fetchAssignedExpertises = () => fetchWorkList("assigned");
export const fetchIncomingExpertises = async (objectCode: string, areaCode: string) => {
  const items = await fetchWorkList("incoming");

  return items.filter((item) =>
    (!objectCode || !item.object_code || item.object_code === objectCode)
    && (!areaCode || !item.area_code || item.area_code === areaCode),
  );
};

