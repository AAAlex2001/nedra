import { API_URL, readErrorMessage } from "@/shared/api";
import type {
  AuditChecklistItem,
  AuditFile,
  AuditPlanInput,
  AuditTeamMember,
  OfferAnswer,
} from "../model/audit";
import type { Expertise } from "../model/types";

const AUDIT_URL = `${API_URL}/v1/audit`;

const JSON_HEADERS = { "Content-Type": "application/json" };

export const createAudit = async (formData: FormData): Promise<Expertise> => {
  const response = await fetch(AUDIT_URL, {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const audit: Expertise = await response.json();

  return audit;
};

export const fetchAuditChecklist = async (): Promise<AuditChecklistItem[]> => {
  const response = await fetch(`${AUDIT_URL}/checklist`);

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const checklist: AuditChecklistItem[] = await response.json();

  return checklist;
};

export const fetchAuditors = async (): Promise<AuditTeamMember[]> => {
  const response = await fetch(`${AUDIT_URL}/auditors`, {
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const auditors: AuditTeamMember[] = await response.json();

  return auditors;
};

export const proposeAuditPrice = async (id: number, price: number): Promise<Expertise> => {
  const response = await fetch(`${AUDIT_URL}/${id}/offer`, {
    method: "POST",
    credentials: "include",
    headers: JSON_HEADERS,
    body: JSON.stringify({ price }),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const audit: Expertise = await response.json();

  return audit;
};

export const answerAuditOffer = async (
  id: number,
  answer: OfferAnswer,
  price: number | null,
): Promise<Expertise> => {
  const response = await fetch(`${AUDIT_URL}/${id}/offer/answer`, {
    method: "POST",
    credentials: "include",
    headers: JSON_HEADERS,
    body: JSON.stringify({ answer, price }),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const audit: Expertise = await response.json();

  return audit;
};

export const answerAuditCounter = async (id: number, accept: boolean): Promise<Expertise> => {
  const response = await fetch(`${AUDIT_URL}/${id}/counter/answer`, {
    method: "POST",
    credentials: "include",
    headers: JSON_HEADERS,
    body: JSON.stringify({ accept }),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const audit: Expertise = await response.json();

  return audit;
};

export const setAuditTeam = async (id: number, userIds: number[]): Promise<Expertise> => {
  const response = await fetch(`${AUDIT_URL}/${id}/team`, {
    method: "PUT",
    credentials: "include",
    headers: JSON_HEADERS,
    body: JSON.stringify({ user_ids: userIds }),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const audit: Expertise = await response.json();

  return audit;
};

export const sendAuditPlan = async (id: number, plan: AuditPlanInput): Promise<Expertise> => {
  const response = await fetch(`${AUDIT_URL}/${id}/plan`, {
    method: "POST",
    credentials: "include",
    headers: JSON_HEADERS,
    body: JSON.stringify(plan),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const audit: Expertise = await response.json();

  return audit;
};

export const approveAuditPlan = async (id: number): Promise<Expertise> => {
  const response = await fetch(`${AUDIT_URL}/${id}/plan/approve`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const audit: Expertise = await response.json();

  return audit;
};

export const requestAuditPlanChanges = async (id: number, comment: string): Promise<Expertise> => {
  const response = await fetch(`${AUDIT_URL}/${id}/plan/changes`, {
    method: "POST",
    credentials: "include",
    headers: JSON_HEADERS,
    body: JSON.stringify({ comment }),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const audit: Expertise = await response.json();

  return audit;
};

export const uploadAuditDocuments = async (id: number, files: AuditFile[]): Promise<Expertise> => {
  const formData = new FormData();

  for (const entry of files) {
    formData.append("files", entry.file);
    formData.append("items", String(entry.item));
  }

  const response = await fetch(`${AUDIT_URL}/${id}/documents`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const audit: Expertise = await response.json();

  return audit;
};

export const auditDocumentsReportUrl = (expertiseId: number): string =>
  `${AUDIT_URL}/${expertiseId}/documents-report`;
