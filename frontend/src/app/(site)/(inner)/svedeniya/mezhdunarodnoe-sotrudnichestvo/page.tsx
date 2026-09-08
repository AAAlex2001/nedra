import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaMezhdunarodnoe from "@/widgets/svedeniya/mezhdunarodnoe-sotrudnichestvo";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata("/svedeniya/mezhdunarodnoe-sotrudnichestvo");

export default function SvedeniyaMezhdunarodnoePage() {
  return (
    <SvedeniyaPage
      activeSlug="mezhdunarodnoe-sotrudnichestvo"
      crumb="Международное сотрудничество"
    >
      <SvedeniyaMezhdunarodnoe />
    </SvedeniyaPage>
  );
}
