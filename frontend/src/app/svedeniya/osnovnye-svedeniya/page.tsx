import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaOsnovnye from "@/widgets/svedeniya/osnovnye-svedeniya";

export const metadata: Metadata = {
  title:
    "Основные сведения — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaOsnovnyePage() {
  return (
    <SvedeniyaPage activeSlug="osnovnye-svedeniya" crumb="Основные сведения">
      <SvedeniyaOsnovnye />
    </SvedeniyaPage>
  );
}
