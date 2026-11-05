import { API_URL } from "@/shared/api";
import type { WorkPaymentsResponse } from "../model/api-responses";
import type { ContractKind, Expertise, ExpertisePayment, ServiceKind } from "../model/types";
import { fetchAudit } from "./read-audit";
import { fetchExpertise } from "./read-expertise";
import { jsonBody, requestJson } from "./request";

export { fetchMyExpertises, fetchAssignedExpertises, fetchIncomingExpertises } from "./work-lists";

export const workPath = (id: number, service: ServiceKind): string =>
  `/${service === "audit" ? "audit" : "expertises"}/${id}`;

export const fetchWork = (id: number, service: ServiceKind): Promise<Expertise> =>
  service === "audit" ? fetchAudit(id) : fetchExpertise(id);

const changeWork = async (
  id: number, service: ServiceKind, action: string, init?: RequestInit,
): Promise<Expertise> => {
  await requestJson(`${workPath(id, service)}/${action}`, { method: "POST", ...init });
  return fetchWork(id, service);
};

export const createExpertise = (formData: FormData): Promise<{ id: number }> =>
  requestJson("/expertises", { method: "POST", body: formData });

export const acceptExpertise = (
  id: number, contractKind: ContractKind | null, service: ServiceKind,
): Promise<Expertise> =>
  changeWork(id, service, "accept", jsonBody({ contract_kind: contractKind }));

export const confirmExpertise = (id: number, service: ServiceKind): Promise<Expertise> =>
  changeWork(id, service, "confirm");

export const createExpertisePayment = (id: number): Promise<ExpertisePayment> =>
  requestJson(`/expertises/${id}/payment`, { method: "POST" });

export const refreshExpertisePayment = async (id: number, service: ServiceKind): Promise<Expertise> => {
  const payments = await requestJson<WorkPaymentsResponse>(`${workPath(id, service)}/payments`);

  for (const stage of [payments.advance, payments.final]) {
    const payment = stage?.payment;

    if (payment && (payment.status === "pending" || payment.status === "waiting_for_capture")) {
      await requestJson(`/payments/${payment.id}/refresh`, { method: "POST" });
    }
  }

  return fetchWork(id, service);
};

export const markConclusionReady = (id: number, service: ServiceKind): Promise<Expertise> =>
  changeWork(id, service, "conclusion-ready");

export const sendRemarks = (id: number, formData: FormData, service: ServiceKind): Promise<Expertise> =>
  changeWork(id, service, "remarks", { body: formData });

export const resubmitDocumentation = (
  id: number, formData: FormData, service: ServiceKind,
): Promise<Expertise> => changeWork(id, service, "revision", { body: formData });

export const sendConclusion = (
  id: number, formData: FormData, service: ServiceKind,
): Promise<Expertise> => changeWork(id, service, "conclusion", { body: formData });

export const acceptWork = (id: number, service: ServiceKind): Promise<Expertise> =>
  changeWork(id, service, "accept-work");

export const expertiseDocumentUrl = (id: number, documentId: number, service: ServiceKind): string =>
  `${API_URL}/v1${workPath(id, service)}/documents/${documentId}`;

export const expertiseSigningUrl = (id: number, kind: "contract" | "nda", service: ServiceKind): string =>
  `${API_URL}/v1${workPath(id, service)}/signing/${kind}`;
