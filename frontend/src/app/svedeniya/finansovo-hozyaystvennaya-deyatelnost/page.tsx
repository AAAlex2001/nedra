import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaFinansovo from "@/widgets/svedeniya/finansovo-hozyaystvennaya-deyatelnost";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata(
  "/svedeniya/finansovo-hozyaystvennaya-deyatelnost",
);

export default function SvedeniyaFinansovoPage() {
  return (
    <SvedeniyaPage
      activeSlug="finansovo-hozyaystvennaya-deyatelnost"
      crumb="Финансово-хозяйственная деятельность"
    >
      <SvedeniyaFinansovo />
    </SvedeniyaPage>
  );
}
