import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaRukovodstvo from "@/widgets/svedeniya/rukovodstvo";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata("/svedeniya/rukovodstvo");

export default function SvedeniyaRukovodstvoPage() {
  return (
    <SvedeniyaPage activeSlug="rukovodstvo" crumb="Руководство">
      <SvedeniyaRukovodstvo />
    </SvedeniyaPage>
  );
}
