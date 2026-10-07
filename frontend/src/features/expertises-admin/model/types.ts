import type {
  ContractKind,
  CustomerType,
  Deadline,
  ExpertiseCompany,
  ExpertiseIndividual,
  ExpertiseStatus,
  ServiceKind,
} from "@/entities/expertise";

export type ExpertiseAdminRecord = {
  id: number;
  service: ServiceKind;
  customer_id: number;
  customer_name: string;
  expert_id: number | null;
  expert_name: string | null;
  object_code: string | null;
  area_code: string | null;
  hazard_class: number | null;
  expert_category: number | null;
  deadline: Deadline | null;
  object_name: string | null;
  contract_kind: ContractKind | null;
  customer_type: CustomerType;
  company: ExpertiseCompany | null;
  individual: ExpertiseIndividual | null;
  comment: string | null;
  status: ExpertiseStatus;
  price: string | null;
  created_at: string;
};

export type ExpertOption = {
  user_id: number;
  full_name: string;
};

export type ExpertiseDraft = {
  status: ExpertiseStatus;
  price: string;
  expertId: string;
  contractKind: ContractKind | "";
};

export type StatusGroup = "waiting" | "work" | "done";

export type StatusFilter = StatusGroup | "all";
