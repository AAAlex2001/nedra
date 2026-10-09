import {
  KINDS_WITH_STO,
  type AuditApplicant,
  type AuditElement,
  type AuditKind,
  type AuditObject,
  type AuditScope,
  type AuditStage,
  type BudgetMode,
  type Negotiation,
  type TimingKind,
} from "@/entities/expertise";
import type { FormErrors } from "./types";

export type AuditForm = {
  applicant: AuditApplicant;
  proxyFile: File | null;
  scope: AuditScope | null;
  objects: AuditObject[];
  fleetCount: string;
  fleetProfile: string;
  multiRegion: boolean | null;
  certificate: File | null;
  stages: AuditStage[];
  kind: AuditKind | null;
  useSto: boolean | null;
  stoName: string;
  stoFile: File | null;
  elements: AuditElement[];
  timing: TimingKind | "";
  start: string;
  end: string;
  budget: BudgetMode;
  negotiation: Negotiation | null;
};

export type AuditBlockProps = {
  form: AuditForm;
  errors: FormErrors;
  onChange: (form: AuditForm) => void;
};

export const EMPTY_OBJECT: AuditObject = {
  reg_number: "",
  name: "",
  hazard_class: "",
  address: "",
  industry: "",
  hazard_signs: [],
};

export const needsSto = (kind: AuditKind | null): boolean =>
  kind !== null && KINDS_WITH_STO.includes(kind);

export const emptyAuditForm = (fullName: string, phone: string, email: string): AuditForm => ({
  applicant: {
    full_name: fullName,
    position: "",
    organization: "",
    inn: "",
    phone,
    email,
    by_proxy: false,
  },
  proxyFile: null,
  scope: null,
  objects: [EMPTY_OBJECT],
  fleetCount: "",
  fleetProfile: "",
  multiRegion: null,
  certificate: null,
  stages: [],
  kind: null,
  useSto: null,
  stoName: "",
  stoFile: null,
  elements: [],
  timing: "",
  start: "",
  end: "",
  budget: "custom",
  negotiation: null,
});

export const toAuditDetails = (form: AuditForm) => {
  const allObjects = form.scope === "all";
  const customTiming = form.timing === "custom";

  return {
    applicant: form.applicant,
    scope: form.scope,
    objects: allObjects ? [] : form.objects,
    fleet: allObjects
      ? { count: Number(form.fleetCount), profile: form.fleetProfile, multi_region: form.multiRegion }
      : null,
    stages: form.stages,
    params: {
      kind: form.kind,
      use_sto: needsSto(form.kind) ? form.useSto : null,
      sto_name: form.useSto ? form.stoName : null,
      elements: form.kind === "selective" ? form.elements : [],
    },
    timing: {
      kind: form.timing,
      start: customTiming ? form.start : null,
      end: customTiming ? form.end : null,
    },
    budget: { mode: form.budget, negotiation: form.negotiation },
  };
};
