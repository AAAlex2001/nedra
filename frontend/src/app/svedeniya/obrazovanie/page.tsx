import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaObrazovanie from "@/widgets/svedeniya/obrazovanie";

export const metadata: Metadata = {
  title: "Образование — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaObrazovaniePage() {
  return (
    <SvedeniyaPage activeSlug="obrazovanie" crumb="Образование">
      <SvedeniyaObrazovanie />
    </SvedeniyaPage>
  );
}
