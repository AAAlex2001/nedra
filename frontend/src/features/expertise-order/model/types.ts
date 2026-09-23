export type RequirementMode = "hazard" | "category" | "unknown";

export type Deadline = "today" | "three_days" | "week" | "any";

export type SubmitStatus = "idle" | "loading" | "success" | "error";

export type OrderState = {
  objectCode: string;
  mode: RequirementMode;
  hazardClass: number | null;
  category: number | null;
  areaCode: string;
  deadline: Deadline | null;
  files: File[];
  companyCard: File | null;
  comment: string;
  status: SubmitStatus;
  error: string | null;
};

export type OrderAction =
  | { type: "object/select"; code: string }
  | { type: "mode/set"; mode: RequirementMode }
  | { type: "hazard/select"; value: number }
  | { type: "category/select"; value: number }
  | { type: "area/select"; code: string }
  | { type: "deadline/select"; value: Deadline }
  | { type: "files/add"; files: File[] }
  | { type: "files/remove"; index: number }
  | { type: "card/set"; file: File }
  | { type: "card/remove" }
  | { type: "comment/change"; value: string }
  | { type: "submit/start" }
  | { type: "submit/success" }
  | { type: "submit/error"; message: string }
  | { type: "success/close" };
