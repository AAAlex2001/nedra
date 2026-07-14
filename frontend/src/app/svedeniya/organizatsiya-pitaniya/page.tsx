import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaPitanie from "@/widgets/svedeniya/organizatsiya-pitaniya";

export const metadata: Metadata = {
  title:
    "Организация питания — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaPitaniePage() {
  return (
    <SvedeniyaPage
      activeSlug="organizatsiya-pitaniya"
      crumb="Организация питания в образовательной организации"
    >
      <SvedeniyaPitanie />
    </SvedeniyaPage>
  );
}
