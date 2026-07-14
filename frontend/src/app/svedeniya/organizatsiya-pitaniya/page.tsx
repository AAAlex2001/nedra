import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaPitanie from "@/widgets/svedeniya/organizatsiya-pitaniya";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata("/svedeniya/organizatsiya-pitaniya");

export default function SvedeniyaPitaniePage() {
  return (
    <SvedeniyaPage
      activeSlug="organizatsiya-pitaniya"
      crumb="Организация питания в образовательной организации"
    >
      <SvedeniyaPitanie />
    </SvedeniyaPage>
  );
}
