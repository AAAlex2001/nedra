import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaMaterialno from "@/widgets/svedeniya/materialno-tehnicheskoe-obespechenie";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata(
  "/svedeniya/materialno-tehnicheskoe-obespechenie",
);

export default function SvedeniyaMaterialnoPage() {
  return (
    <SvedeniyaPage
      activeSlug="materialno-tehnicheskoe-obespechenie"
      crumb="Материально-техническое обеспечение и оснащённость образовательного процесса. Доступная среда"
    >
      <SvedeniyaMaterialno />
    </SvedeniyaPage>
  );
}
