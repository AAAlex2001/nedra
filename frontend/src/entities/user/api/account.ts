import { API_URL, readErrorMessage } from "@/shared/api";
import type { User } from "../model/types";

export type ProfilePayload = {
  full_name: string;
  phone: string;
};

const send = async (path: string, method: "PATCH" | "POST", body: object): Promise<Response> => {
  const response = await fetch(`${API_URL}/v1/auth/${path}`, {
    method,
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  return response;
};

export const updateProfile = async (payload: ProfilePayload): Promise<User> => {
  const response = await send("me", "PATCH", payload);
  const user: User = await response.json();

  return user;
};

export const requestEmailChange = async (email: string): Promise<void> => {
  await send("me/email", "POST", { email });
};

export const confirmEmailChange = async (code: string): Promise<User> => {
  const response = await send("me/email/confirm", "POST", { code });
  const user: User = await response.json();

  return user;
};
