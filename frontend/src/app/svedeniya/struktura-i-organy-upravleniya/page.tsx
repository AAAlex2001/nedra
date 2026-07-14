import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaStruktura from "@/widgets/svedeniya/struktura";

export const metadata: Metadata = {
  title:
    "Структура и органы управления — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaStrukturaPage() {
  return (
    <SvedeniyaPage
      activeSlug="struktura-i-organy-upravleniya"
      crumb="Структура и органы управления образовательной организацией"
    >
      <SvedeniyaStruktura />
    </SvedeniyaPage>
  );
}
