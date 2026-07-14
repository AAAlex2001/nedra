import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaRukovodstvo from "@/widgets/svedeniya/rukovodstvo";

export const metadata: Metadata = {
  title: "Руководство — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaRukovodstvoPage() {
  return (
    <SvedeniyaPage activeSlug="rukovodstvo" crumb="Руководство">
      <SvedeniyaRukovodstvo />
    </SvedeniyaPage>
  );
}
