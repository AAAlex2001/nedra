import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaPedagogicheskiySostav from "@/widgets/svedeniya/pedagogicheskiy-sostav";

export const metadata: Metadata = {
  title:
    "Педагогический состав — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaPedagogicheskiySostavPage() {
  return (
    <SvedeniyaPage activeSlug="pedagogicheskiy-sostav" crumb="Педагогический состав">
      <SvedeniyaPedagogicheskiySostav />
    </SvedeniyaPage>
  );
}
