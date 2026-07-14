import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaObrazovanie from "@/widgets/svedeniya/obrazovanie";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata("/svedeniya/obrazovanie");

export default function SvedeniyaObrazovaniePage() {
  return (
    <SvedeniyaPage activeSlug="obrazovanie" crumb="Образование">
      <SvedeniyaObrazovanie />
    </SvedeniyaPage>
  );
}
