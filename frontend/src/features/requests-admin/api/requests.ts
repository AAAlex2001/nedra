import type { RequestRecord } from "@/entities/request";
import { readErrorMessage } from "@/shared/api";

export const fetchRequests = async (
  basePath: string,
): Promise<RequestRecord[]> => {
  const response = await fetch(`${basePath}/api/requests`, {
    cache: "no-store",
  });

  if (!response.ok) throw new Error(await readErrorMessage(response));

  return (await response.json()) as RequestRecord[];
};
