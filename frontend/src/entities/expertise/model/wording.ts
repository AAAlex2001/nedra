import {
  EXPERTISE_STATUS_LABELS,
  type Expertise,
  type ExpertiseStatus,
  type ServiceKind,
} from "./types";

export type ServiceWording = {
  title: string;
  executor: string;
  executorLower: string;
  work: string;
  documents: string;
  result: string;
  resultLower: string;
  resultReady: string;
  resultSent: string;
  remarksStage: string;
  revisionStage: string;
};

const EXPERTISE_WORDING: ServiceWording = {
  title: "Экспертиза промышленной безопасности",
  executor: "Эксперт",
  executorLower: "эксперт",
  work: "экспертизу",
  documents: "документацию",
  result: "Заключение",
  resultLower: "заключение",
  resultReady: "Заключение готово",
  resultSent: "Заключение отправлено",
  remarksStage: "Рекомендации эксперта",
  revisionStage: "Исправленная документация",
};

const AUDIT_WORDING: ServiceWording = {
  title: "Аудит системы управления промышленной безопасностью",
  executor: "Аудитор",
  executorLower: "аудитор",
  work: "аудит",
  documents: "документы",
  result: "Отчёт об аудите",
  resultLower: "отчёт об аудите",
  resultReady: "Отчёт готов",
  resultSent: "Отчёт отправлен",
  remarksStage: "Замечания аудитора",
  revisionStage: "Исправленные документы",
};

export const SERVICE_LABELS: Record<ServiceKind, string> = {
  expertise: "Экспертиза",
  audit: "Аудит СУПБ",
};

export const isAudit = (expertise: Expertise): boolean => expertise.service === "audit";

export const wordingFor = (expertise: Expertise): ServiceWording =>
  isAudit(expertise) ? AUDIT_WORDING : EXPERTISE_WORDING;

export const AUDIT_STATUS_LABELS: Record<ExpertiseStatus, string> = {
  new: "Ждёт аудитора",
  consultation: "Нужна консультация",
  offer: "Аудитор предложил цену",
  counter: "Заказчик предложил цену",
  expert_ready: "Аудитор готов",
  contract: "Договор заключён",
  plan: "Аванс оплачен, готовится План",
  plan_review: "Согласование Плана аудита",
  in_progress: "План согласован, в работе",
  remarks: "Замечания аудитора",
  conclusion_ready: "Отчёт готов",
  paid: "Оплачено полностью",
  sent: "Отчёт отправлен",
  accepted: "Работа принята",
};

export const statusLabel = (expertise: Expertise): string =>
  isAudit(expertise)
    ? AUDIT_STATUS_LABELS[expertise.status]
    : EXPERTISE_STATUS_LABELS[expertise.status];
