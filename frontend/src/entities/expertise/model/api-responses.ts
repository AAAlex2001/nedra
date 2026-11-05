import type { AuditDetails, AuditPlan, AuditTeamMember } from "./audit";
import type {
  ContractKind, CustomerType, Deadline, ExpertiseCompany, ExpertiseIndividual,
  ExpertiseInvoice, ExpertisePayment, ExpertiseResult, ExpertiseStatus,
} from "./types";

export type WorkSummaryResponse = {
  id: number;
  customer_id: number;
  expert_id?: number | null;
  lead_id?: number | null;
  status: ExpertiseStatus;
  price: string | null;
  created_at: string;
};

export type WorkDatesResponse = {
  created_at: string;
  conclusion_ready_at: string | null;
  sent_at: string | null;
  accepted_at: string | null;
};

export type ExpertiseResponse = {
  id: number;
  customer_id: number;
  expert_id: number | null;
  status: ExpertiseStatus;
  result: ExpertiseResult | null;
  object: {
    name: string | null;
    object_code: string | null;
    area_code: string | null;
    hazard_class: number | null;
    expert_category: number | null;
  };
  conditions: { price: string | null; deadline: Deadline | null; comment: string | null };
  dates: WorkDatesResponse & { expert_ready_at: string | null };
};

export type AuditResponse = {
  id: number;
  customer_id: number;
  lead_id: number | null;
  status: ExpertiseStatus;
  result: ExpertiseResult | null;
  conditions: {
    customer_budget: string | null;
    agreed_price: string | null;
    offer_price: string | null;
    counter_price: string | null;
    negotiation_allowed: boolean;
    comment: string | null;
  };
  dates: WorkDatesResponse & { lead_ready_at: string | null };
};

export type ContractResponse = {
  id: number;
  kind: ContractKind | null;
  confirmed_at: string | null;
};

type PaymentStageResponse = { paid_at: string | null; payment: ExpertisePayment | null };

export type WorkPaymentsResponse = {
  advance: PaymentStageResponse | null;
  final: PaymentStageResponse | null;
  invoice: ExpertiseInvoice | null;
};

export type ExpertiseParticipantsResponse = {
  customer: { id: number; full_name: string };
  expert: { id: number; full_name: string } | null;
  customer_type: CustomerType;
  company: ExpertiseCompany | null;
  individual: ExpertiseIndividual | null;
};

export type AuditCustomerResponse = {
  id: number;
  full_name: string;
  customer_type: CustomerType;
  company: ExpertiseCompany | null;
};

export type AuditApplicationResponse = { object_name: string | null; details: AuditDetails | null };
export type AuditPlanResponse = {
  schedule: AuditPlan | null;
  comment: string | null;
  sent_at: string | null;
  approved_at: string | null;
};
export type AuditTeamResponse = AuditTeamMember[];

