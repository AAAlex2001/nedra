export type AuditChecklistItem = {
  number: number;
  title: string;
};

export type AuditFile = {
  item: number;
  file: File;
};

export const AUDIT_CHECKLIST_SIZE = 47;

export const MIN_AUDIT_PRICE = 100000;

export const AUDIT_FILES_ACCEPT = ".pdf,.sig,.p7s,.jpg,.jpeg,.png,.heic,.mp4,.mov";

export type AuditScope = "one" | "all" | "selected";

export const AUDIT_SCOPE_LABELS: Record<AuditScope, string> = {
  one: "Аудит СУПБ в отношении одного ОПО",
  all: "Аудит СУПБ в отношении всех ОПО",
  selected: "Аудит СУПБ выборочных ОПО",
};

export type AuditStage = "planning" | "documents" | "onsite" | "report";

export const AUDIT_STAGES: AuditStage[] = ["planning", "documents", "onsite", "report"];

export const AUDIT_STAGE_LABELS: Record<AuditStage, string> = {
  planning:
    "Этап 1: Планирование аудита СУПБ (формирование группы по проведению аудита, подготовка программы аудита)",
  documents:
    "Этап 2: Документарный этап (оценка проектной, организационно-распорядительной, локальной и иной документации на соответствие требованиям нормативных правовых актов в области промышленной безопасности)",
  onsite:
    "Этап 3: Выездной этап (выезд группы аудиторов на ОПО для оценки соблюдения требований, консультирование работников, проведение заключительного совещания с руководством)",
  report:
    "Этап 4: Оформление итогового отчета (анализ и оценка соблюдения требований, разработка корректирующих мероприятий и мер по совершенствованию СУПБ)",
};

export const AUDIT_STAGE_TITLES: Record<AuditStage, string> = {
  planning: "Планирование аудита",
  documents: "Документарный этап",
  onsite: "Выездной этап",
  report: "Оформление итогового отчёта",
};

export type HazardClass = "I" | "II" | "III" | "IV";

export const HAZARD_CLASSES: HazardClass[] = ["I", "II", "III", "IV"];

export type HazardSign = "substances" | "pressure" | "lifting" | "melts" | "mining" | "grain";

export const HAZARD_SIGNS: HazardSign[] = [
  "substances",
  "pressure",
  "lifting",
  "melts",
  "mining",
  "grain",
];

export const HAZARD_SIGN_LABELS: Record<HazardSign, string> = {
  substances:
    "Получение, использование, переработка, образование, хранение, транспортирование, уничтожение опасных веществ",
  pressure:
    "Оборудование, работающее под избыточным давлением более 0,07 МПа (пар, газ, вода при температуре более 115 °C, иные жидкости выше температуры кипения)",
  lifting:
    "Стационарно установленные грузоподъёмные механизмы, эскалаторы в метрополитенах, канатные дороги, фуникулёры",
  melts:
    "Получение, транспортирование, использование расплавов чёрных и цветных металлов и сплавов на их основе (оборудование на 500 кг расплава и более)",
  mining: "Горные работы, работы по обогащению полезных ископаемых",
  grain:
    "Хранение или переработка растительного сырья с образованием взрывоопасных пылевоздушных смесей, хранение зерна и продуктов его переработки",
};

export type AuditKind = "basic" | "interim" | "selective" | "consultation";

export const AUDIT_KINDS: AuditKind[] = ["basic", "interim", "selective", "consultation"];

export const AUDIT_KIND_LABELS: Record<AuditKind, string> = {
  basic:
    "Базовый (полный) аудит СУПБ – оценка всех элементов системы (рекомендуется 1 раз в 3 года)",
  interim:
    "Промежуточный аудит СУПБ – оценка выполнения корректирующих мероприятий по результатам базового аудита",
  selective: "Выборочный аудит отдельных элементов СУПБ",
  consultation: "Нужна консультация для определения типа аудита",
};

export const AUDIT_KIND_TITLES: Record<AuditKind, string> = {
  basic: "Базовый (полный) аудит СУПБ",
  interim: "Промежуточный аудит СУПБ",
  selective: "Выборочный аудит отдельных элементов СУПБ",
  consultation: "Нужна консультация для определения типа аудита",
};

export const KINDS_WITH_STO: AuditKind[] = ["basic", "interim"];

export type AuditElement =
  | "identification"
  | "documentation"
  | "production_control"
  | "documents_compliance"
  | "risk_measures"
  | "incidents"
  | "emergency"
  | "insurance"
  | "personnel"
  | "contractors"
  | "work_conditions"
  | "equipment"
  | "declaration"
  | "justification"
  | "intrusion"
  | "instruments"
  | "resources"
  | "other";

export const AUDIT_ELEMENTS: AuditElement[] = [
  "identification",
  "documentation",
  "production_control",
  "documents_compliance",
  "risk_measures",
  "incidents",
  "emergency",
  "insurance",
  "personnel",
  "contractors",
  "work_conditions",
  "equipment",
  "declaration",
  "justification",
  "intrusion",
  "instruments",
  "resources",
  "other",
];

export const AUDIT_ELEMENT_LABELS: Record<AuditElement, string> = {
  identification: "Идентификация ОПО",
  documentation: "Документационное обеспечение и функционирование СУПБ",
  production_control: "Организация и эффективность производственного контроля",
  documents_compliance:
    "Соответствие организационно-распорядительной, технической, разрешительной, эксплуатационной, учетной и иной документации, определение недостающей документации",
  risk_measures:
    "Планирование и реализация мер по предупреждению и (или) снижению риска аварий, несчастных случаев и инцидентов на ОПО",
  incidents: "Учет и расследование инцидентов и несчастных случаев",
  emergency:
    "Готовность организации к действиям по локализации и ликвидации последствий аварий на ОПО",
  insurance:
    "Обязательное страхование гражданской ответственности в соответствии с законодательством РФ",
  personnel:
    "Аттестация, обучение, допуск персонала (включая работников подрядных организаций)",
  contractors: "Допуск и контроль подрядных организаций на ОПО",
  work_conditions: "Обеспечение условий труда и безопасности ведения работ на ОПО",
  equipment: "Эксплуатация технических устройств (ТУ), зданий и сооружений (ЗиС) на ОПО",
  declaration: "Декларация промышленной безопасности ОПО",
  justification: "Обоснование безопасности ОПО",
  intrusion: "Принятие мер по предотвращению проникновения на ОПО посторонних лиц",
  instruments:
    "Обеспечение наличия и функционирования необходимых приборов и систем контроля за производственными процессами в соответствии с установленными требованиями",
  resources:
    "Наличие и достаточность ресурсов (материальных, трудовых, временных) для выполнения задач в области промышленной безопасности",
  other:
    "Иная деятельность, связанная с обеспечением выполнения требований к СУПБ, установленных пунктом 4 статьи 11 Федерального закона № 116-ФЗ",
};

export type TimingKind = "custom" | "month" | "this_quarter" | "next_quarter" | "studying";

export const TIMING_KINDS: TimingKind[] = [
  "custom",
  "month",
  "this_quarter",
  "next_quarter",
  "studying",
];

export const TIMING_LABELS: Record<TimingKind, string> = {
  custom: "Свой срок",
  month: "В течение 1 месяца (срочно)",
  this_quarter: "В текущем квартале",
  next_quarter: "В следующем квартале",
  studying: "Пока изучаем предложение",
};

export type BudgetMode = "custom" | "none";

export const BUDGET_LABELS: Record<BudgetMode, string> = {
  custom: "Указать свою сумму",
  none: "Бюджет не установлен (требуется детальный расчет на основании заполненной заявки)",
};

export type Negotiation = "yes" | "no" | "on_scope";

export const NEGOTIATIONS: Negotiation[] = ["yes", "no", "on_scope"];

export const NEGOTIATION_LABELS: Record<Negotiation, string> = {
  yes: "Да, стоимость подлежит обсуждению",
  no: "Нет, бюджет строго фиксирован",
  on_scope: "Готовы обсудить при расширении объема услуг или изменении сроков",
};

export type AuditApplicant = {
  full_name: string;
  position: string;
  organization: string;
  inn: string;
  phone: string;
  email: string;
  by_proxy: boolean;
};

export type AuditObject = {
  reg_number: string;
  name: string;
  hazard_class: HazardClass | "";
  address: string;
  industry: string;
  hazard_signs: HazardSign[];
};

export type AuditFleet = {
  count: number;
  profile: string;
  multi_region: boolean;
};

export type AuditParams = {
  kind: AuditKind;
  use_sto: boolean | null;
  sto_name: string | null;
  elements: AuditElement[];
};

export type AuditTiming = {
  kind: TimingKind;
  start: string | null;
  end: string | null;
};

export type AuditBudget = {
  mode: BudgetMode;
  negotiation: Negotiation;
};

export type AuditDetails = {
  applicant: AuditApplicant;
  scope: AuditScope;
  objects: AuditObject[];
  fleet: AuditFleet | null;
  stages: AuditStage[];
  params: AuditParams;
  timing: AuditTiming;
  budget: AuditBudget;
};

export type AuditPlanInput = {
  documents_start: string;
  documents_end: string;
  onsite_start: string | null;
  onsite_end: string | null;
  meetings: boolean;
  opening_at: string | null;
  closing_at: string | null;
  meeting_link: string | null;
  workshops: string | null;
  interviewees: string;
};

export type AuditPlan = AuditPlanInput & {
  version: number;
};

export type AuditTeamMember = {
  user_id: number;
  full_name: string;
  areas: string[];
  lead: boolean;
};

export type OfferAnswer = "accept" | "counter" | "decline";

export const negotiable = (details: AuditDetails | null): boolean =>
  details !== null && details.budget.negotiation !== "no";
