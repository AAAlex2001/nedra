import { API_URL } from "./config";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export const readErrorMessage = async (response: Response): Promise<string> => {
  try {
    const body = await response.json();

    if (typeof body.detail === "string") return body.detail;
  } catch {
    return `Ошибка ${response.status}`;
  }

  return `Ошибка ${response.status}`;
};

export const postJson = async <T>(path: string, payload: unknown): Promise<T> => {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new ApiError(response.status, await readErrorMessage(response));
  }

  return (await response.json()) as T;
};
