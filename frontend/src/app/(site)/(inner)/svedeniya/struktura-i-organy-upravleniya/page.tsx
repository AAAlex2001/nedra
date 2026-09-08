import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaStruktura from "@/widgets/svedeniya/struktura";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata("/svedeniya/struktura-i-organy-upravleniya");

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
