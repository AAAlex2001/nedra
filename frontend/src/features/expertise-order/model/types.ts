import type { ContractKind, ExpertiseCompany } from "@/entities/expertise";

export type RequirementMode = "hazard" | "category" | "unknown";

export type Deadline = "today" | "three_days" | "week" | "any";

export type SubmitStatus = "idle" | "loading" | "success" | "error";

export type CompanyField = keyof ExpertiseCompany;

export type CompanyFields = Record<CompanyField, string>;

export type OrderState = {
  objectCode: string;
  contractKind: ContractKind | "";
  objectName: string;
  mode: RequirementMode;
  hazardClass: number | null;
  category: number | null;
  areaCode: string;
  deadline: Deadline | null;
  company: CompanyFields;
  files: File[];
  companyCard: File | null;
  comment: string;
  status: SubmitStatus;
  error: string | null;
};

export type OrderAction =
  | { type: "object/select"; code: string }
  | { type: "kind/select"; kind: ContractKind | "" }
  | { type: "objectName/change"; value: string }
  | { type: "mode/set"; mode: RequirementMode }
  | { type: "hazard/select"; value: number }
  | { type: "category/select"; value: number }
  | { type: "area/select"; code: string }
  | { type: "deadline/select"; value: Deadline }
  | { type: "company/change"; field: CompanyField; value: string }
  | { type: "company/fill"; company: ExpertiseCompany }
  | { type: "files/add"; files: File[] }
  | { type: "files/remove"; index: number }
  | { type: "card/set"; file: File }
  | { type: "card/remove" }
  | { type: "comment/change"; value: string }
  | { type: "submit/start" }
  | { type: "submit/success" }
  | { type: "submit/error"; message: string }
  | { type: "success/close" };
