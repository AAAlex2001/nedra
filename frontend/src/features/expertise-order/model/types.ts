import type {
  ContractKind,
  CustomerType,
  ExpertiseCompany,
  ExpertiseIndividual,
} from "@/entities/expertise";

export type RequirementMode = "hazard" | "category" | "unknown";

export type Deadline = "today" | "three_days" | "week" | "any";

export type SubmitStatus = "idle" | "loading" | "success" | "error";

export type CompanyField = keyof ExpertiseCompany;

export type CompanyFields = Record<CompanyField, string>;

export type IndividualField = keyof ExpertiseIndividual;

export type IndividualFields = Record<IndividualField, string>;

export type AuditFile = {
  item: number;
  file: File;
};

export type OrderState = {
  objectCode: string;
  contractKind: ContractKind | "";
  objectName: string;
  mode: RequirementMode;
  hazardClass: number | null;
  category: number | null;
  areaCode: string;
  deadline: Deadline | null;
  price: string;
  customerType: CustomerType;
  company: CompanyFields;
  individual: IndividualFields;
  files: File[];
  auditFiles: AuditFile[];
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
  | { type: "price/change"; value: string }
  | { type: "customer/select"; customerType: CustomerType }
  | { type: "company/change"; field: CompanyField; value: string }
  | { type: "company/fill"; company: ExpertiseCompany }
  | { type: "individual/change"; field: IndividualField; value: string }
  | { type: "individual/fill"; individual: ExpertiseIndividual }
  | { type: "files/add"; files: File[] }
  | { type: "files/remove"; index: number }
  | { type: "auditFiles/add"; item: number; files: File[] }
  | { type: "auditFiles/remove"; target: AuditFile }
  | { type: "card/set"; file: File }
  | { type: "card/remove" }
  | { type: "comment/change"; value: string }
  | { type: "submit/start" }
  | { type: "submit/success" }
  | { type: "submit/error"; message: string }
  | { type: "success/close" };
