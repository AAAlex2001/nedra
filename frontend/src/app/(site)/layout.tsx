import { cookies } from "next/headers";
import { SessionProvider, type User } from "@/entities/user";
import { AuthModalProvider } from "@/features/auth";
import { internalFetch } from "@/shared/api/server";
import Footer from "@/widgets/footer";
import Header from "@/widgets/header";

const AUTH_COOKIE = "access_token";

const loadCurrentUser = async (): Promise<User | null> => {
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

export default async function SiteLayout({ children }: { children: React.ReactNode }) {
  const user = await loadCurrentUser();

  return (
    <SessionProvider initialUser={user}>
      <AuthModalProvider>
        <Header />
        {children}
        <Footer />
      </AuthModalProvider>
    </SessionProvider>
  );
}
