import type { Attestation, CommissionApplicationRecord } from "@/entities/commission";
import { API_URL, readErrorMessage } from "@/shared/api";

export const submitCommissionApplication = async (
  fullName: string,
  attestations: Attestation[],
): Promise<CommissionApplicationRecord> => {
  const response = await fetch(`${API_URL}/v1/commission/applications`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ full_name: fullName.trim(), attestations }),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const created: CommissionApplicationRecord = await response.json();

  return created;
};
