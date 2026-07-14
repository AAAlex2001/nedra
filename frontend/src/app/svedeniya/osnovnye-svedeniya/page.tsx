import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaOsnovnye from "@/widgets/svedeniya/osnovnye-svedeniya";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata("/svedeniya/osnovnye-svedeniya");

export default function SvedeniyaOsnovnyePage() {
  return (
    <SvedeniyaPage activeSlug="osnovnye-svedeniya" crumb="Основные сведения">
      <SvedeniyaOsnovnye />
    </SvedeniyaPage>
  );
}
