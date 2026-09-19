import type { ExpertApplicationRecord } from "@/entities/expert";
import { readErrorMessage } from "@/shared/api";

export const fetchApplications = async (
  basePath: string,
): Promise<ExpertApplicationRecord[]> => {
  const response = await fetch(`${basePath}/api/experts/applications`, {
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const items: ExpertApplicationRecord[] = await response.json();

  return items;
};

export const approveApplication = async (
  basePath: string,
  id: number,
): Promise<ExpertApplicationRecord> => {
  const response = await fetch(`${basePath}/api/experts/applications/${id}/approve`, {
    method: "POST",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const updated: ExpertApplicationRecord = await response.json();

  return updated;
};

export const rejectApplication = async (
  basePath: string,
  id: number,
  comment: string,
): Promise<ExpertApplicationRecord> => {
  const response = await fetch(`${basePath}/api/experts/applications/${id}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ comment }),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const updated: ExpertApplicationRecord = await response.json();

  return updated;
};

export const scanUrl = (basePath: string, applicationId: number, certificateId: number) =>
  `${basePath}/api/experts/applications/${applicationId}/certificates/${certificateId}/scan`;
