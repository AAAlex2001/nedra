import { readErrorMessage } from "@/shared/api";

export type ExpertUpdate = {
  full_name: string;
  phone: string;
  directions: string[];
};

export type CertificateUpdate = {
  area_code: string;
  object_code: string;
  category: number;
  valid_until: string;
  number: string;
};

export const updateExpert = async (
  basePath: string,
  userId: number,
  payload: ExpertUpdate,
): Promise<void> => {
  const response = await fetch(`${basePath}/api/experts/${userId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }
};

export const createCertificate = async (
  basePath: string,
  userId: number,
  payload: CertificateUpdate,
): Promise<void> => {
  const response = await fetch(`${basePath}/api/experts/${userId}/certificates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }
};

export const updateCertificate = async (
  basePath: string,
  userId: number,
  certificateId: number,
  payload: CertificateUpdate,
): Promise<void> => {
  const response = await fetch(
    `${basePath}/api/experts/${userId}/certificates/${certificateId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }
};

export const deleteCertificate = async (
  basePath: string,
  userId: number,
  certificateId: number,
): Promise<void> => {
  const response = await fetch(
    `${basePath}/api/experts/${userId}/certificates/${certificateId}`,
    { method: "DELETE" },
  );

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }
};
