import { API_URL, readErrorMessage } from "@/shared/api";
import type { ExpertCatalog, ExpertProfile } from "../model/types";

export type ApplicationCreated = {
  id: number;
  status: string;
};

export const fetchExpertCatalog = async (): Promise<ExpertCatalog> => {
  const response = await fetch(`${API_URL}/v1/experts/catalog`);

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const catalog: ExpertCatalog = await response.json();

  return catalog;
};

export const submitExpertApplication = async (
  formData: FormData,
): Promise<ApplicationCreated> => {
  const response = await fetch(`${API_URL}/v1/experts/applications`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const created: ApplicationCreated = await response.json();

  return created;
};

export const myCertificateScanUrl = (certificateId: number): string =>
  `${API_URL}/v1/experts/me/certificates/${certificateId}/scan`;

export type CertificateInput = {
  area_code: string;
  object_code: string;
  category: number;
  valid_until: string;
  number: string;
};

const sendMyCertificate = async (
  url: string,
  method: "POST" | "PATCH" | "DELETE",
  payload: CertificateInput | null,
): Promise<ExpertProfile> => {
  const response = await fetch(url, {
    method,
    credentials: "include",
    headers: payload ? { "Content-Type": "application/json" } : undefined,
    body: payload ? JSON.stringify(payload) : undefined,
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const profile: ExpertProfile = await response.json();

  return profile;
};

export const addMyCertificate = (payload: CertificateInput): Promise<ExpertProfile> =>
  sendMyCertificate(`${API_URL}/v1/experts/me/certificates`, "POST", payload);

export const updateMyCertificate = (
  certificateId: number,
  payload: CertificateInput,
): Promise<ExpertProfile> =>
  sendMyCertificate(`${API_URL}/v1/experts/me/certificates/${certificateId}`, "PATCH", payload);

export const deleteMyCertificate = (certificateId: number): Promise<ExpertProfile> =>
  sendMyCertificate(`${API_URL}/v1/experts/me/certificates/${certificateId}`, "DELETE", null);

export const fetchExpertProfile = async (): Promise<ExpertProfile> => {
  const response = await fetch(`${API_URL}/v1/experts/me`, {
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const profile: ExpertProfile = await response.json();

  return profile;
};
