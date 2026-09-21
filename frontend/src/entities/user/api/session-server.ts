import { cookies } from "next/headers";
import { internalFetch } from "@/shared/api/server";
import type { User } from "../model/types";

const AUTH_COOKIE = "access_token";

export const hasSessionCookie = async (): Promise<boolean> => {
  const store = await cookies();

  return store.get(AUTH_COOKIE) !== undefined;
};

export const getCurrentUser = async (): Promise<User | null> => {
  const store = await cookies();
  const token = store.get(AUTH_COOKIE);

  if (!token) return null;

  try {
    const response = await internalFetch("/v1/auth/me", {
      headers: { Cookie: `${AUTH_COOKIE}=${token.value}` },
      cache: "no-store",
    });

    if (!response.ok) return null;

    const user: User = await response.json();

    return user;
  } catch {
    return null;
  }
};
