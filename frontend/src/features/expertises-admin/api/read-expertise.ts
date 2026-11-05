import "server-only";

import type {
  ContractResponse, ExpertiseParticipantsResponse, ExpertiseResponse,
} from "@/entities/expertise/model/api-responses";
import type { ExpertiseAdminRecord } from "../model/types";
import { readAdminJson } from "./admin-request";

export const readAdminExpertise = async (id: number): Promise<ExpertiseAdminRecord> => {
  const path = `/expertises/${id}`;
  const [expertise, participants, contract] = await Promise.all([
    readAdminJson<ExpertiseResponse>(path),
    readAdminJson<ExpertiseParticipantsResponse>(`${path}/participants`),
    readAdminJson<ContractResponse | null>(`${path}/contract`),
  ]);

  return {
    id: expertise.id,
    service: "expertise",
    status: expertise.status,
    customer_id: expertise.customer_id,
    customer_name: participants.customer.full_name,
    customer_type: participants.customer_type,
    company: participants.company,
    individual: participants.individual,
    expert_id: expertise.expert_id,
    expert_name: participants.expert?.full_name ?? null,
    ...expertise.object,
    object_name: expertise.object.name,
    ...expertise.conditions,
    created_at: expertise.dates.created_at,
    contract_kind: contract?.kind ?? null,
    audit_details: null,
  };
};

