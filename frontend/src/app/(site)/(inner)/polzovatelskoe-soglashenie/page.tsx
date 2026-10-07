import { LEGAL_PAGES } from "@/shared/config/legal";
import { buildMetadata } from "@/shared/config/seo";
import LegalPage, { USER_AGREEMENT } from "@/widgets/legal-document";

export const metadata = buildMetadata(LEGAL_PAGES.agreement.href);

export default function UserAgreementPage() {
  return <LegalPage document={USER_AGREEMENT} label={LEGAL_PAGES.agreement.label} />;
}
