import { cookies } from "next/headers";

const AUTH_COOKIE = "access_token";

export const hasSessionCookie = async (): Promise<boolean> => {
  const store = await cookies();

  return store.get(AUTH_COOKIE) !== undefined;
};
