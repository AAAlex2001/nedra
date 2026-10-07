import { LEGAL_PAGES } from "@/shared/config/legal";
import { buildMetadata } from "@/shared/config/seo";
import LegalPage, { PERSONAL_DATA_CONSENT } from "@/widgets/legal-document";

export const metadata = buildMetadata(LEGAL_PAGES.consent.href);

export default function PersonalDataConsentPage() {
  return <LegalPage document={PERSONAL_DATA_CONSENT} label={LEGAL_PAGES.consent.label} />;
}
