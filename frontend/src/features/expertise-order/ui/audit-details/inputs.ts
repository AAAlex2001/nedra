import {
  AUDIT_ELEMENTS,
  AUDIT_ELEMENT_LABELS,
  AUDIT_KINDS,
  AUDIT_KIND_LABELS,
  AUDIT_SCOPE_LABELS,
  BUDGET_LABELS,
  HAZARD_CLASSES,
  HAZARD_SIGNS,
  HAZARD_SIGN_LABELS,
  NEGOTIATIONS,
  NEGOTIATION_LABELS,
  TIMING_KINDS,
  TIMING_LABELS,
  type AuditScope,
  type BudgetMode,
} from "@/entities/expertise";

export type ApplicantField = "full_name" | "position" | "organization" | "inn" | "phone" | "email";

export type ObjectTextField = "reg_number" | "name" | "address" | "industry";

export type Answer = "yes" | "no";

export const toAnswer = (value: boolean | null): Answer | null => {
  if (value === null) return null;
  if (value) return "yes";

  return "no";
};

type ApplicantInput = {
  field: ApplicantField;
  label: string;
  placeholder: string;
  type?: "text" | "tel" | "email";
  numeric?: boolean;
};

type ObjectInput = {
  field: ObjectTextField;
  label: string;
  placeholder: string;
  wide?: boolean;
};

export const APPLICANT_INPUTS: ApplicantInput[] = [
  { field: "full_name", label: "ФИО представителя", placeholder: "Иванов Иван Иванович" },
  { field: "position", label: "Должность", placeholder: "Главный инженер" },
  { field: "organization", label: "Наименование организации", placeholder: "ООО «Ромашка»" },
  { field: "inn", label: "ИНН организации", placeholder: "10 или 12 цифр", numeric: true },
  { field: "phone", label: "Контактный телефон", placeholder: "+7 999 000-00-00", type: "tel" },
  { field: "email", label: "Корпоративный e-mail", placeholder: "ivanov@company.ru", type: "email" },
];

export const PROXY_OPTIONS: { value: Answer; label: string }[] = [
  { value: "no", label: "Я руководитель" },
  { value: "yes", label: "По доверенности" },
];

export const OBJECT_INPUTS: ObjectInput[] = [
  { field: "reg_number", label: "Регистрационный номер ОПО", placeholder: "А59-12345-0001" },
  { field: "name", label: "Наименование ОПО", placeholder: "Сеть газопотребления" },
  {
    field: "address",
    label: "Адрес (местонахождение) ОПО",
    placeholder: "г. Новосибирск, ул. Ленина, д. 1",
    wide: true,
  },
  {
    field: "industry",
    label: "Отраслевая специфика / вид деятельности на ОПО",
    placeholder: "Газопотребление",
    wide: true,
  },
];

export const HAZARD_CLASS_OPTIONS = HAZARD_CLASSES.map((value) => ({ value, label: value }));

export const HAZARD_SIGN_OPTIONS = HAZARD_SIGNS.map((value) => ({
  value,
  label: HAZARD_SIGN_LABELS[value],
}));

const SCOPES: AuditScope[] = ["one", "all", "selected"];

export const SCOPE_OPTIONS = SCOPES.map((scope) => ({
  value: scope,
  label: AUDIT_SCOPE_LABELS[scope],
}));

export const YES_NO_OPTIONS: { value: Answer; label: string }[] = [
  { value: "yes", label: "Да" },
  { value: "no", label: "Нет" },
];

export const KIND_OPTIONS = AUDIT_KINDS.map((value) => ({
  value,
  label: AUDIT_KIND_LABELS[value],
}));

export const STO_OPTIONS: { value: Answer; label: string }[] = [
  { value: "yes", label: "Да, в организации действует СТО по аудиту СУПБ" },
  {
    value: "no",
    label:
      "Нет, аудит СУПБ проводится только на соответствие требованиям законодательства (116-ФЗ, ПП РФ 1243, ФНП, Приказ 318)",
  },
];

export const ELEMENT_OPTIONS = AUDIT_ELEMENTS.map((value) => ({
  value,
  label: AUDIT_ELEMENT_LABELS[value],
}));

export const TIMING_OPTIONS = TIMING_KINDS.map((value) => ({
  value,
  label: TIMING_LABELS[value],
}));

const BUDGETS: BudgetMode[] = ["custom", "none"];

export const BUDGET_OPTIONS = BUDGETS.map((value) => ({ value, label: BUDGET_LABELS[value] }));

export const NEGOTIATION_OPTIONS = NEGOTIATIONS.map((value) => ({
  value,
  label: NEGOTIATION_LABELS[value],
}));
