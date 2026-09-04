import { API_URL } from "./config";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

type FastApiDetail = { detail?: string | { msg?: string }[] };

/** FastAPI кладёт причину в detail: строкой при HTTPException, массивом при 422. */
const extractDetail = (body: FastApiDetail): string | null => {
  if (typeof body.detail === "string") return body.detail;

  if (Array.isArray(body.detail)) {
    const messages = body.detail
      .map((item) => item?.msg)
      .filter((msg): msg is string => Boolean(msg));

    if (messages.length > 0) return messages.join(", ");
  }

  return null;
};

export const postJson = async <T>(path: string, payload: unknown): Promise<T> => {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let detail: string | null = null;

    try {
      detail = extractDetail(await response.json());
    } catch {
      detail = null;
    }

    throw new ApiError(response.status, detail ?? `Сервер ответил ${response.status}`);
  }

  return (await response.json()) as T;
};
