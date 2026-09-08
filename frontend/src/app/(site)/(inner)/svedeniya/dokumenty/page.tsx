import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaDocuments from "@/widgets/svedeniya/documents";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata("/svedeniya/dokumenty");

export default function SvedeniyaDokumentyPage() {
  return (
    <SvedeniyaPage activeSlug="dokumenty" crumb="Документы">
      <SvedeniyaDocuments />
    </SvedeniyaPage>
  );
}
