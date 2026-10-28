import type { UserRole } from "@/entities/user";

export type SectionIcon =
  | "inbox"
  | "work"
  | "done"
  | "expert"
  | "audit"
  | "invoice"
  | "act"
  | "account"
  | "bell";

export type SectionGroup = "Работа" | "Документы" | "Аккаунт";

export type CabinetSection = {
  key: string;
  label: string;
  icon: SectionIcon;
  group: SectionGroup;
  href?: string;
};

export const SECTION_GROUPS: SectionGroup[] = ["Работа", "Документы", "Аккаунт"];

const CUSTOMER_SECTIONS: CabinetSection[] = [
  { key: "mine", label: "В работе", icon: "work", group: "Работа" },
  { key: "finished", label: "Завершённые", icon: "done", group: "Работа" },
  { key: "blits-ekspert", label: "Блиц-эксперт", icon: "expert", group: "Работа", href: "/blits-ekspert" },
  { key: "blits-audit", label: "Блиц-аудит", icon: "audit", group: "Работа", href: "/blits-audit" },
  { key: "invoices", label: "Счета", icon: "invoice", group: "Документы" },
  { key: "acts", label: "Акты", icon: "act", group: "Документы" },
  { key: "account", label: "Мои данные", icon: "account", group: "Аккаунт" },
  { key: "notifications", label: "Уведомления", icon: "bell", group: "Аккаунт" },
];

const EXPERT_SECTIONS: CabinetSection[] = [
  { key: "incoming", label: "Входящие заявки", icon: "inbox", group: "Работа" },
  { key: "assigned", label: "В работе", icon: "work", group: "Работа" },
  { key: "finished", label: "Завершённые", icon: "done", group: "Работа" },
  { key: "account", label: "Мои данные", icon: "account", group: "Аккаунт" },
  { key: "notifications", label: "Уведомления", icon: "bell", group: "Аккаунт" },
];

export const sectionsFor = (role: UserRole): CabinetSection[] =>
  role === "expert" ? EXPERT_SECTIONS : CUSTOMER_SECTIONS;

export const tabSections = (sections: CabinetSection[]): CabinetSection[] =>
  sections.filter((section) => !section.href);

export const sectionHref = (section: CabinetSection): string =>
  section.href ?? `/kabinet?tab=${section.key}`;
