import "server-only";

import type { ExpertiseAdminRecord } from "../model/types";
import { readAdminJson } from "./admin-request";
import { readAdminAudit, type AdminAuditSummary } from "./read-audit";
import { readAdminExpertise } from "./read-expertise";

export const readAdminWorks = async (): Promise<ExpertiseAdminRecord[]> => {
  const [expertises, audits] = await Promise.all([
    readAdminJson<{ id: number }[]>("/expertises"),
    readAdminJson<AdminAuditSummary[]>("/audits"),
  ]);
  const records = await Promise.all([
    ...expertises.map((item) => readAdminExpertise(item.id)),
    ...audits.map(readAdminAudit),
  ]);

  return records.sort((first, second) =>
    second.created_at.localeCompare(first.created_at) || second.id - first.id,
  );
};

