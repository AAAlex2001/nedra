import type { RequestRecord } from "@/entities/request";
import { readErrorMessage } from "@/shared/api";

export const fetchRequests = async (
  basePath: string,
): Promise<RequestRecord[]> => {
  const response = await fetch(`${basePath}/api/requests`, {
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const requests: RequestRecord[] = await response.json();

  return requests;
};

export const deleteRequest = async (
  basePath: string,
  id: number,
): Promise<void> => {
  const response = await fetch(`${basePath}/api/requests/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }
};
