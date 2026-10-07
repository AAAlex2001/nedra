import { LEGAL_PAGES } from "@/shared/config/legal";
import { buildMetadata } from "@/shared/config/seo";
import LegalPage, { PRIVACY_POLICY } from "@/widgets/legal-document";

export const metadata = buildMetadata(LEGAL_PAGES.privacy.href);

export default function PrivacyPolicyPage() {
  return <LegalPage document={PRIVACY_POLICY} label={LEGAL_PAGES.privacy.label} />;
}
