import type {
  AuditApplicationResponse, AuditCustomerResponse, AuditPlanResponse, AuditResponse,
  AuditTeamResponse, ContractResponse, WorkPaymentsResponse,
} from "../model/api-responses";
import type { Expertise, ExpertiseDocument, ExpertiseRemark } from "../model/types";
import { requestJson } from "./request";

export const fetchAudit = async (id: number): Promise<Expertise> => {
  const path = `/audit/${id}`;
  const [audit, customer, application, team, plan, documents, remarks, contract, payments] = await Promise.all([
    requestJson<AuditResponse>(path),
    requestJson<AuditCustomerResponse>(`${path}/customer`),
    requestJson<AuditApplicationResponse | null>(`${path}/application`),
    requestJson<AuditTeamResponse>(`${path}/team`),
    requestJson<AuditPlanResponse | null>(`${path}/plan`),
    requestJson<ExpertiseDocument[]>(`${path}/documents`),
    requestJson<ExpertiseRemark[]>(`${path}/remarks`),
    requestJson<ContractResponse | null>(`${path}/contract`),
    requestJson<WorkPaymentsResponse>(`${path}/payments`),
  ]);

  return {
    id: audit.id,
    service: "audit",
    customer_id: audit.customer_id,
    customer_name: customer.full_name,
    customer_type: customer.customer_type,
    company: customer.company,
    individual: null,
    expert_id: audit.lead_id,
    expert_name: team.find((member) => member.user_id === audit.lead_id)?.full_name ?? null,
    object_name: application?.object_name ?? null,
    object_code: null,
    area_code: null,
    hazard_class: null,
    expert_category: null,
    deadline: null,
    price: audit.conditions.agreed_price ?? audit.conditions.customer_budget,
    comment: audit.conditions.comment,
    offer_price: audit.conditions.offer_price,
    counter_price: audit.conditions.counter_price,
    ...audit.dates,
    expert_ready_at: audit.dates.lead_ready_at,
    status: audit.status,
    result: audit.result,
    contract_kind: contract?.kind ?? "audit",
    contract_at: contract?.confirmed_at ?? null,
    advance_payment: payments.advance?.payment ?? null,
    advance_paid_at: payments.advance?.paid_at ?? null,
    final_payment: payments.final?.payment ?? null,
    final_paid_at: payments.final?.paid_at ?? null,
    invoice: payments.invoice,
    audit_details: application?.details ?? null,
    audit_plan: plan?.schedule ?? null,
    plan_comment: plan?.comment ?? null,
    plan_sent_at: plan?.sent_at ?? null,
    plan_approved_at: plan?.approved_at ?? null,
    team,
    documents,
    remarks,
  };
};

