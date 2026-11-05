import { API_URL, readErrorMessage } from "@/shared/api";

export const requestJson = async <T>(path: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(`${API_URL}/v1${path}`, {
    credentials: "include",
    cache: "no-store",
    ...init,
  });

  if (!response.ok) throw new Error(await readErrorMessage(response));

  return response.json() as Promise<T>;
};

export const jsonBody = (payload: unknown): RequestInit => ({
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});

