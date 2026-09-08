import SvedeniyaPage from "@/shared/ui/svedeniya-page";
import SvedeniyaPedagogicheskiySostav from "@/widgets/svedeniya/pedagogicheskiy-sostav";
import { buildMetadata } from "@/shared/config/seo";

export const metadata = buildMetadata("/svedeniya/pedagogicheskiy-sostav");

export default function SvedeniyaPedagogicheskiySostavPage() {
  return (
    <SvedeniyaPage activeSlug="pedagogicheskiy-sostav" crumb="Педагогический состав">
      <SvedeniyaPedagogicheskiySostav />
    </SvedeniyaPage>
  );
}
