import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaStipendii from "@/widgets/svedeniya/stipendii-i-mery-podderzhki";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata("/svedeniya/stipendii-i-mery-podderzhki");

export default function SvedeniyaStipendiiPage() {
  return (
    <SvedeniyaPage
      activeSlug="stipendii-i-mery-podderzhki"
      crumb="Стипендии и меры поддержки обучающихся"
    >
      <SvedeniyaStipendii />
    </SvedeniyaPage>
  );
}
