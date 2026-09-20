import { API_URL, readErrorMessage } from "@/shared/api";
import type { User } from "../model/types";

export type RegisterPayload = {
  email: string;
  password: string;
  full_name: string;
  phone: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export const registerUser = async (payload: RegisterPayload): Promise<User> => {
  const response = await fetch(`${API_URL}/v1/auth/register`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const user: User = await response.json();

  return user;
};

export const loginUser = async (payload: LoginPayload): Promise<User> => {
  const response = await fetch(`${API_URL}/v1/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const user: User = await response.json();

  return user;
};

export const logoutUser = async (): Promise<void> => {
  const response = await fetch(`${API_URL}/v1/auth/logout`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }
};

