export type PersonalFields = {
  fullName: string;
  email: string;
  phone: string;
  password: string;
};

export type CertificateDraft = {
  areaCode: string;
  objectCode: string;
  category: number | null;
  validUntil: string;
  number: string;
};

export type CertificateItem = CertificateDraft & {
  key: number;
};

export type SubmitStatus = "idle" | "loading" | "success" | "error";

export type ApplicationFormState = {
  fields: PersonalFields;
  directions: string[];
  draft: CertificateDraft;
  certificates: CertificateItem[];
  nextKey: number;
  status: SubmitStatus;
  error: string | null;
};

export type ApplicationFormAction =
  | { type: "field/change"; field: keyof PersonalFields; value: string }
  | { type: "direction/toggle"; code: string }
  | { type: "draft/area"; code: string }
  | { type: "draft/object"; code: string }
  | { type: "draft/category"; category: number }
  | { type: "draft/date"; value: string }
  | { type: "draft/number"; value: string }
  | { type: "certificate/add" }
  | { type: "certificate/remove"; key: number }
  | { type: "submit/start" }
  | { type: "submit/success" }
  | { type: "submit/error"; message: string }
  | { type: "success/close" };
