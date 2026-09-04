export type RequestFields = {
  name: string;
  telephone: string;
  email: string;
  companyName: string;
  inn: string;
  comment: string;
};

export type RequestStatus = "idle" | "loading" | "success" | "error";

export type RequestFormState = {
  directionId: string;
  serviceId: string;
  fields: RequestFields;
  status: RequestStatus;
  error: string | null;
};

export type RequestFormAction =
  | { type: "direction/select"; id: string }
  | { type: "service/select"; id: string }
  | { type: "field/change"; field: keyof RequestFields; value: string }
  | { type: "submit/start" }
  | { type: "submit/success" }
  | { type: "submit/error"; message: string }
  | { type: "form/reset" };
