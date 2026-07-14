import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaMezhdunarodnoe from "@/widgets/svedeniya/mezhdunarodnoe-sotrudnichestvo";

export const metadata: Metadata = {
  title:
    "Международное сотрудничество — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaMezhdunarodnoePage() {
  return (
    <SvedeniyaPage
      activeSlug="mezhdunarodnoe-sotrudnichestvo"
      crumb="Международное сотрудничество"
    >
      <SvedeniyaMezhdunarodnoe />
    </SvedeniyaPage>
  );
}
