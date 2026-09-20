import { API_URL, readErrorMessage } from "@/shared/api";
import type { Expertise, ExpertisePayment } from "../model/types";

export const createExpertise = async (formData: FormData): Promise<Expertise> => {
  const response = await fetch(`${API_URL}/v1/expertise`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const expertise: Expertise = await response.json();

  return expertise;
};

export const fetchMyExpertises = async (): Promise<Expertise[]> => {
  const response = await fetch(`${API_URL}/v1/expertise/my`, {
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const items: Expertise[] = await response.json();

  return items;
};

export const fetchIncomingExpertises = async (
  objectCode: string,
  areaCode: string,
): Promise<Expertise[]> => {
  const params = new URLSearchParams();
  if (objectCode) params.set("object_code", objectCode);
  if (areaCode) params.set("area_code", areaCode);

  const query = params.toString();
  const url = query
    ? `${API_URL}/v1/expertise/incoming?${query}`
    : `${API_URL}/v1/expertise/incoming`;

  const response = await fetch(url, {
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const items: Expertise[] = await response.json();

  return items;
};

export const fetchAssignedExpertises = async (): Promise<Expertise[]> => {
  const response = await fetch(`${API_URL}/v1/expertise/assigned`, {
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const items: Expertise[] = await response.json();

  return items;
};

export const acceptExpertise = async (id: number): Promise<Expertise> => {
  const response = await fetch(`${API_URL}/v1/expertise/${id}/accept`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const expertise: Expertise = await response.json();

  return expertise;
};

export const confirmExpertise = async (id: number): Promise<Expertise> => {
  const response = await fetch(`${API_URL}/v1/expertise/${id}/confirm`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const expertise: Expertise = await response.json();

  return expertise;
};

export const createExpertisePayment = async (id: number): Promise<ExpertisePayment> => {
  const response = await fetch(`${API_URL}/v1/expertise/${id}/payment`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const payment: ExpertisePayment = await response.json();

  return payment;
};

export const refreshExpertisePayment = async (id: number): Promise<Expertise> => {
  const response = await fetch(`${API_URL}/v1/expertise/${id}/payment/refresh`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const expertise: Expertise = await response.json();

  return expertise;
};

export const markConclusionReady = async (id: number): Promise<Expertise> => {
  const response = await fetch(`${API_URL}/v1/expertise/${id}/conclusion-ready`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const expertise: Expertise = await response.json();

  return expertise;
};

export const sendRemarks = async (id: number, formData: FormData): Promise<Expertise> => {
  const response = await fetch(`${API_URL}/v1/expertise/${id}/remarks`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const expertise: Expertise = await response.json();

  return expertise;
};

export const resubmitDocumentation = async (
  id: number,
  formData: FormData,
): Promise<Expertise> => {
  const response = await fetch(`${API_URL}/v1/expertise/${id}/revision`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const expertise: Expertise = await response.json();

  return expertise;
};

export const sendConclusion = async (id: number, formData: FormData): Promise<Expertise> => {
  const response = await fetch(`${API_URL}/v1/expertise/${id}/conclusion`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const expertise: Expertise = await response.json();

  return expertise;
};

export const acceptWork = async (id: number): Promise<Expertise> => {
  const response = await fetch(`${API_URL}/v1/expertise/${id}/accept-work`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const expertise: Expertise = await response.json();

  return expertise;
};

export const expertiseDocumentUrl = (expertiseId: number, documentId: number): string =>
  `${API_URL}/v1/expertise/${expertiseId}/documents/${documentId}`;
