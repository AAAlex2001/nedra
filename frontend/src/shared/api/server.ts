import { API_INTERNAL_URL } from "./config";

const adminHeaders = (): Record<string, string> => ({
  "X-Admin-Token": process.env.ADMIN_API_TOKEN ?? "",
});

export const internalFetch = (path: string, init?: RequestInit) =>
  fetch(`${API_INTERNAL_URL}${path}`, init);

export const adminFetch = (path: string, init: RequestInit = {}) =>
  fetch(`${API_INTERNAL_URL}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      ...adminHeaders(),
      ...((init.headers as Record<string, string> | undefined) ?? {}),
    },
  });

export type Loaded<T> = {
  data: T;
  error: string | null;
};

export const loadAdmin = async <T,>(path: string, fallback: T): Promise<Loaded<T>> => {
  try {
    const response = await adminFetch(path);

    if (!response.ok) {
      return { data: fallback, error: `Бэкенд ответил ${response.status}` };
    }

    return { data: (await response.json()) as T, error: null };
  } catch {
    return { data: fallback, error: "Бэкенд недоступен" };
  }
};

export const adminBasePath = () => `/${process.env.ADMIN_PATH ?? ""}`;
