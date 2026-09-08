import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaPlatnye from "@/widgets/svedeniya/platnye-obrazovatelnye-uslugi";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata("/svedeniya/platnye-obrazovatelnye-uslugi");

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
