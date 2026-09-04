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
  directionId: string | null;
  serviceId: string | null;
  fields: RequestFields;
  status: RequestStatus;
  error: string | null;
  /** Ошибки показываем только после первой попытки отправки. */
  submitted: boolean;
};

export type RequestFormAction =
  | { type: "direction/select"; id: string }
  | { type: "service/select"; id: string }
  | { type: "field/change"; field: keyof RequestFields; value: string }
  | { type: "submit/start" }
  | { type: "submit/success" }
  | { type: "submit/error"; message: string }
  | { type: "form/reset" };

export type FieldErrors = Partial<
  Record<keyof RequestFields | "service", string>
>;
