import type {
  ContractResponse, ExpertiseParticipantsResponse, ExpertiseResponse, WorkPaymentsResponse,
} from "../model/api-responses";
import type { Expertise, ExpertiseDocument, ExpertiseRemark } from "../model/types";
import { requestJson } from "./request";

export const fetchExpertise = async (id: number): Promise<Expertise> => {
  const path = `/expertises/${id}`;
  const [expertise, participants, documents, remarks, contract, payments] = await Promise.all([
    requestJson<ExpertiseResponse>(path),
    requestJson<ExpertiseParticipantsResponse>(`${path}/participants`),
    requestJson<ExpertiseDocument[]>(`${path}/documents`),
    requestJson<ExpertiseRemark[]>(`${path}/remarks`),
    requestJson<ContractResponse | null>(`${path}/contract`),
    requestJson<WorkPaymentsResponse>(`${path}/payments`),
  ]);

  return {
    id: expertise.id,
    service: "expertise",
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
    ...expertise.dates,
    status: expertise.status,
    result: expertise.result,
    contract_kind: contract?.kind ?? null,
    contract_at: contract?.confirmed_at ?? null,
    advance_payment: payments.advance?.payment ?? null,
    advance_paid_at: payments.advance?.paid_at ?? null,
    final_payment: payments.final?.payment ?? null,
    final_paid_at: payments.final?.paid_at ?? null,
    invoice: payments.invoice,
    documents,
    remarks,
    audit_details: null,
    audit_plan: null,
    plan_comment: null,
    plan_sent_at: null,
    plan_approved_at: null,
    offer_price: null,
    counter_price: null,
    team: [],
  };
};

