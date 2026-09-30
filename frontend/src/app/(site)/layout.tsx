import { SessionProvider } from "@/entities/user";
import { getCurrentUser } from "@/entities/user/api/session-server";
import { AuthModalProvider } from "@/features/auth";
import { CommissionPopupProvider } from "@/features/commission-application";
import CommissionPopup from "@/widgets/commission-popup";
import Footer from "@/widgets/footer";
import GuestBar from "@/widgets/guest-bar";
import Header from "@/widgets/header";

export default async function SiteLayout({ children }: { children: React.ReactNode }) {
  const user = await getCurrentUser();

  return (
    <SessionProvider initialUser={user}>
      <AuthModalProvider>
        <CommissionPopupProvider>
          <Header />
          {children}
          <Footer />
          <GuestBar />
          <CommissionPopup />
        </CommissionPopupProvider>
      </AuthModalProvider>
    </SessionProvider>
  );
}
