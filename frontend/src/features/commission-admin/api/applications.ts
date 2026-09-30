import type { CommissionApplicationRecord } from "@/entities/commission";
import { readErrorMessage } from "@/shared/api";

export const fetchCommissionApplications = async (
  basePath: string,
): Promise<CommissionApplicationRecord[]> => {
  const response = await fetch(`${basePath}/api/commission`, { cache: "no-store" });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const applications: CommissionApplicationRecord[] = await response.json();

  return applications;
};

export const deleteCommissionApplication = async (basePath: string, id: number): Promise<void> => {
  const response = await fetch(`${basePath}/api/commission/${id}`, { method: "DELETE" });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }
};
