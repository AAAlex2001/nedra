import "server-only";

import { readErrorMessage } from "@/shared/api";
import { adminFetch } from "@/shared/api/server";

export const readAdminJson = async <T>(path: string): Promise<T> => {
  const response = await adminFetch(`/v1/admin${path}`);

  if (!response.ok) throw new Error(await readErrorMessage(response));

  return response.json() as Promise<T>;
};

