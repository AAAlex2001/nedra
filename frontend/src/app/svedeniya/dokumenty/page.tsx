import type { Metadata } from "next";
import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaDocuments from "@/widgets/svedeniya/documents";

export const metadata: Metadata = {
  title: "Документы — Сведения об образовательной организации | НПИ «Недра»",
};

export default function SvedeniyaDokumentyPage() {
  return (
    <SvedeniyaPage activeSlug="dokumenty" crumb="Документы">
      <SvedeniyaDocuments />
    </SvedeniyaPage>
  );
}
