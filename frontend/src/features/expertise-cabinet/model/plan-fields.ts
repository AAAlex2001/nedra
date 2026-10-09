import type { AuditPlan, AuditPlanInput, Expertise } from "@/entities/expertise";
import { toDateTimeInput } from "@/shared/lib/date";

export type PlanFields = {
  documentsStart: string;
  documentsEnd: string;
  onsiteStart: string;
  onsiteEnd: string;
  meetings: boolean;
  openingAt: string;
  closingAt: string;
  meetingLink: string;
  workshops: string;
  interviewees: string;
};

const EMPTY_PLAN: PlanFields = {
  documentsStart: "",
  documentsEnd: "",
  onsiteStart: "",
  onsiteEnd: "",
  meetings: true,
  openingAt: "",
  closingAt: "",
  meetingLink: "",
  workshops: "",
  interviewees: "",
};

export const hasOnsite = (expertise: Expertise): boolean => {
  if (!expertise.audit_details) return false;

  return expertise.audit_details.stages.includes("onsite");
};

const savedPlanFields = (plan: AuditPlan): PlanFields => ({
  documentsStart: plan.documents_start,
  documentsEnd: plan.documents_end,
  onsiteStart: plan.onsite_start ?? "",
  onsiteEnd: plan.onsite_end ?? "",
  meetings: plan.meetings,
  openingAt: toDateTimeInput(plan.opening_at),
  closingAt: toDateTimeInput(plan.closing_at),
  meetingLink: plan.meeting_link ?? "",
  workshops: plan.workshops ?? "",
  interviewees: plan.interviewees,
});

export const initialPlanFields = (expertise: Expertise): PlanFields => {
  if (expertise.audit_plan) return savedPlanFields(expertise.audit_plan);

  return EMPTY_PLAN;
};

export const planProblem = (fields: PlanFields, onsite: boolean): string | null => {
  if (!fields.documentsStart || !fields.documentsEnd) return "Укажите даты документарного этапа";
  if (fields.documentsStart > fields.documentsEnd) return "Документарный этап начинается позже окончания";
  if (onsite && (!fields.onsiteStart || !fields.onsiteEnd)) return "Укажите даты выездного этапа";
  if (onsite && fields.onsiteStart > fields.onsiteEnd) return "Выездной этап начинается позже окончания";
  if (fields.meetings && !fields.openingAt) return "Укажите время вступительного совещания";
  if (fields.meetings && !fields.closingAt) return "Укажите время заключительного совещания";
  if (!fields.interviewees.trim()) return "Укажите должностных лиц для интервью";

  return null;
};

const toIso = (value: string): string | null => {
  if (!value) return null;

  return new Date(value).toISOString();
};

export const toPlanInput = (fields: PlanFields, onsite: boolean): AuditPlanInput => ({
  documents_start: fields.documentsStart,
  documents_end: fields.documentsEnd,
  onsite_start: onsite ? fields.onsiteStart : null,
  onsite_end: onsite ? fields.onsiteEnd : null,
  meetings: fields.meetings,
  opening_at: fields.meetings ? toIso(fields.openingAt) : null,
  closing_at: fields.meetings ? toIso(fields.closingAt) : null,
  meeting_link: fields.meetingLink || null,
  workshops: onsite ? fields.workshops : null,
  interviewees: fields.interviewees,
});
