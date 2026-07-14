import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaMaterialno from "@/widgets/svedeniya/materialno-tehnicheskoe-obespechenie";

export const metadata: Metadata = {
  title:
    "Материально-техническое обеспечение — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaMaterialnoPage() {
  return (
    <SvedeniyaPage
      activeSlug="materialno-tehnicheskoe-obespechenie"
      crumb="Материально-техническое обеспечение и оснащённость образовательного процесса. Доступная среда"
    >
      <SvedeniyaMaterialno />
    </SvedeniyaPage>
  );
}
