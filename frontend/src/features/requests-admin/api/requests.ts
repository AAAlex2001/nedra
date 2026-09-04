import type { RequestRecord } from "@/entities/request";
import { readErrorMessage } from "@/shared/api";

const ADMIN_API = "/admin/api/requests";

export const fetchRequests = async (): Promise<RequestRecord[]> => {
  const response = await fetch(ADMIN_API, { cache: "no-store" });

  if (!response.ok) throw new Error(await readErrorMessage(response));

  return (await response.json()) as RequestRecord[];
};
