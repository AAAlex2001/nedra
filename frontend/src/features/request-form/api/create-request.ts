import { API_URL, readErrorMessage } from "@/shared/api";
import type { RequestFields } from "../model/types";

export type CreatedRequest = {
  request_id: number;
  direction: number;
  created_at: string;
};

export const createRequest = async (
  fields: RequestFields,
  activity: number,
): Promise<CreatedRequest> => {
  const response = await fetch(`${API_URL}/v1/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: fields.name.trim(),
      telephone: fields.telephone.trim(),
      email: fields.email.trim(),
      activity,
      company_name: fields.companyName.trim() || null,
      inn: fields.inn.trim() || null,
      comment: fields.comment.trim(),
    }),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const created: CreatedRequest = await response.json();

  return created;
};
