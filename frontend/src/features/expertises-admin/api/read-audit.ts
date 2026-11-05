import "server-only";

import type {
  AuditApplicationResponse, AuditCustomerResponse, AuditResponse,
} from "@/entities/expertise/model/api-responses";
import type { ExpertiseAdminRecord } from "../model/types";
import { readAdminJson } from "./admin-request";

export type AdminAuditSummary = { id: number; lead_name: string | null };

export const readAdminAudit = async (summary: AdminAuditSummary): Promise<ExpertiseAdminRecord> => {
  const path = `/audits/${summary.id}`;
  const [audit, customer, application] = await Promise.all([
    readAdminJson<AuditResponse>(path),
    readAdminJson<AuditCustomerResponse>(`${path}/customer`),
    readAdminJson<AuditApplicationResponse | null>(`${path}/application`),
  ]);

  return {
    id: audit.id,
    service: "audit",
    status: audit.status,
    customer_id: audit.customer_id,
    customer_name: customer.full_name,
    customer_type: customer.customer_type,
    company: customer.company,
    individual: null,
    expert_id: audit.lead_id,
    expert_name: summary.lead_name,
    object_name: application?.object_name ?? null,
    audit_details: application?.details ?? null,
    object_code: null,
    area_code: null,
    hazard_class: null,
    expert_category: null,
    deadline: null,
    price: audit.conditions.agreed_price ?? audit.conditions.customer_budget,
    comment: audit.conditions.comment,
    created_at: audit.dates.created_at,
    contract_kind: "audit",
  };
};

