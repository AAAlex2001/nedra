import { LEGAL_PAGES } from "@/shared/config/legal";
import { buildMetadata } from "@/shared/config/seo";
import LegalPage, { PUBLIC_OFFER } from "@/widgets/legal-document";

export const metadata = buildMetadata(LEGAL_PAGES.offer.href);

export default function PublicOfferPage() {
  return <LegalPage document={PUBLIC_OFFER} label={LEGAL_PAGES.offer.label} />;
}
