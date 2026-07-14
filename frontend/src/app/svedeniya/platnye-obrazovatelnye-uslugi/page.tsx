import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaPlatnye from "@/widgets/svedeniya/platnye-obrazovatelnye-uslugi";

export const metadata: Metadata = {
  title:
    "Платные образовательные услуги — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaPlatnyePage() {
  return (
    <SvedeniyaPage
      activeSlug="platnye-obrazovatelnye-uslugi"
      crumb="Платные образовательные услуги"
    >
      <SvedeniyaPlatnye />
    </SvedeniyaPage>
  );
}
