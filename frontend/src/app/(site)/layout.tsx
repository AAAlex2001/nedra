import { SessionProvider } from "@/entities/user";
import { getCurrentUser } from "@/entities/user/api/session-server";
import { AuthModalProvider } from "@/features/auth";
import Footer from "@/widgets/footer";
import GuestBar from "@/widgets/guest-bar";
import Header from "@/widgets/header";

export default async function SiteLayout({ children }: { children: React.ReactNode }) {
  const user = await getCurrentUser();

  return (
    <SessionProvider initialUser={user}>
      <AuthModalProvider>
        <Header />
        {children}
        <Footer />
        <GuestBar />
      </AuthModalProvider>
    </SessionProvider>
  );
}
