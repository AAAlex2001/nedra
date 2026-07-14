import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaFinansovo from "@/widgets/svedeniya/finansovo-hozyaystvennaya-deyatelnost";

export const metadata: Metadata = {
  title:
    "Финансово-хозяйственная деятельность — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaFinansovoPage() {
  return (
    <SvedeniyaPage
      activeSlug="finansovo-hozyaystvennaya-deyatelnost"
      crumb="Финансово-хозяйственная деятельность"
    >
      <SvedeniyaFinansovo />
    </SvedeniyaPage>
  );
}
