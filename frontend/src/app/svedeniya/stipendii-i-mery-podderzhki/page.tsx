import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaStipendii from "@/widgets/svedeniya/stipendii-i-mery-podderzhki";

export const metadata: Metadata = {
  title:
    "Стипендии и меры поддержки обучающихся — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaStipendiiPage() {
  return (
    <SvedeniyaPage
      activeSlug="stipendii-i-mery-podderzhki"
      crumb="Стипендии и меры поддержки обучающихся"
    >
      <SvedeniyaStipendii />
    </SvedeniyaPage>
  );
}
