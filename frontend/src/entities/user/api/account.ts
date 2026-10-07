import { API_URL, readErrorMessage } from "@/shared/api";
import type { User } from "../model/types";

export type ProfilePayload = {
  full_name: string;
  phone: string;
};

export class EmailCooldownError extends Error {
  seconds: number;

  constructor(message: string, seconds: number) {
    super(message);
    this.seconds = seconds;
  }
}

const send = async (path: string, method: "PATCH" | "POST", body: object): Promise<Response> => {
  const response = await fetch(`${API_URL}/v1/auth/${path}`, {
    method,
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (response.ok) return response;

  const message = await readErrorMessage(response);
  const retryAfter = Number(response.headers.get("Retry-After"));

  if (response.status === 429 && retryAfter > 0) {
    throw new EmailCooldownError(message, retryAfter);
  }

  throw new Error(message);
};

export const updateProfile = async (payload: ProfilePayload): Promise<User> => {
  const response = await send("me", "PATCH", payload);
  const user: User = await response.json();

  return user;
};

export type EmailCodeSent = {
  email: string;
  resend_in: number;
};

export const requestEmailChange = async (email: string): Promise<EmailCodeSent> => {
  const response = await send("me/email", "POST", { email });
  const sent: EmailCodeSent = await response.json();

  return sent;
};

export const confirmEmailChange = async (code: string): Promise<User> => {
  const response = await send("me/email/confirm", "POST", { code });
  const user: User = await response.json();

  return user;
};
