export type AttestationDraft = {
  areaCode: string;
  objectCode: string;
  category: number | null;
};

export type AttestationItem = {
  key: number;
  areaCode: string;
  objectCode: string;
  category: number;
};

export type ApplicationStatus = "idle" | "loading" | "success" | "error";

export type ApplicationState = {
  fullName: string;
  draft: AttestationDraft;
  items: AttestationItem[];
  nextKey: number;
  status: ApplicationStatus;
  error: string | null;
};

export type ApplicationAction =
  | { type: "name/change"; value: string }
  | { type: "draft/area"; code: string }
  | { type: "draft/object"; code: string }
  | { type: "draft/category"; category: number }
  | { type: "item/add" }
  | { type: "item/remove"; key: number }
  | { type: "submit/start" }
  | { type: "submit/success" }
  | { type: "submit/error"; message: string };
