export type ExpertiseStatus =
  | "new"
  | "expert_ready"
  | "contract"
  | "in_progress"
  | "remarks"
  | "conclusion_ready"
  | "paid"
  | "sent"
  | "accepted";

export type ExpertiseResult = "positive" | "negative" | "remarks";

export type PaymentStatus = "pending" | "waiting_for_capture" | "succeeded" | "canceled";

export type ExpertisePayment = {
  id: number;
  amount: string;
  status: PaymentStatus;
  confirmation_url: string | null;
  paid_at: string | null;
};

export type ExpertiseDocument = {
  id: number;
  kind: string;
  original_name: string;
  size: number;
  content_type: string;
  created_at: string;
};

export type ExpertiseRemark = {
  id: number;
  text: string | null;
  response_text: string | null;
  created_at: string;
  resolved_at: string | null;
  documents: ExpertiseDocument[];
};

export type Expertise = {
  id: number;
  customer_id: number;
  customer_name: string;
  expert_id: number | null;
  expert_name: string | null;
  object_code: string;
  area_code: string;
  hazard_class: number | null;
  expert_category: number;
  comment: string | null;
  status: ExpertiseStatus;
  result: ExpertiseResult | null;
  price: string | null;
  advance_payment: ExpertisePayment | null;
  final_payment: ExpertisePayment | null;
  created_at: string;
  expert_ready_at: string | null;
  contract_at: string | null;
  advance_paid_at: string | null;
  conclusion_ready_at: string | null;
  final_paid_at: string | null;
  sent_at: string | null;
  accepted_at: string | null;
  documents: ExpertiseDocument[];
  remarks: ExpertiseRemark[];
};

export const EXPERTISE_STATUS_LABELS: Record<ExpertiseStatus, string> = {
  new: "Ждёт эксперта",
  expert_ready: "Эксперт готов",
  contract: "Договор заключён",
  in_progress: "В работе",
  remarks: "Замечания эксперта",
  conclusion_ready: "Заключение готово",
  paid: "Оплачено полностью",
  sent: "Заключение отправлено",
  accepted: "Работа принята",
};

export type ExpertiseStatusTone = "wait" | "work" | "alert" | "review" | "done";

export const EXPERTISE_STATUS_TONES: Record<ExpertiseStatus, ExpertiseStatusTone> = {
  new: "wait",
  expert_ready: "work",
  contract: "work",
  in_progress: "work",
  remarks: "alert",
  conclusion_ready: "work",
  paid: "work",
  sent: "review",
  accepted: "done",
};

export const EXPERTISE_RESULT_LABELS: Record<ExpertiseResult, string> = {
  positive: "Положительное",
  negative: "Отрицательное",
  remarks: "С замечаниями",
};

export const EXPERTISE_STEPS: { status: ExpertiseStatus; label: string }[] = [
  { status: "new", label: "Заявка" },
  { status: "expert_ready", label: "Эксперт" },
  { status: "contract", label: "Договор" },
  { status: "in_progress", label: "Аванс" },
  { status: "conclusion_ready", label: "Заключение" },
  { status: "paid", label: "Остаток" },
  { status: "sent", label: "Отправлено" },
  { status: "accepted", label: "Принято" },
];

export const stepIndex = (status: ExpertiseStatus): number => {
  if (status === "remarks") {
    return EXPERTISE_STEPS.findIndex((step) => step.status === "in_progress");
  }

  return EXPERTISE_STEPS.findIndex((step) => step.status === status);
};

export const hasPendingPayment = (expertise: Expertise): boolean => {
  const payments = [expertise.advance_payment, expertise.final_payment];

  return payments.some((payment) => payment !== null && payment.status === "pending");
};
