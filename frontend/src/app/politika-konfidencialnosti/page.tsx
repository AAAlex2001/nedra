import { buildMetadata } from "@/shared/config/seo";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import RequestSection from "@/widgets/landing/request-form";
import PrivacyPolicy from "@/widgets/privacy-policy";
import styles from "./page.module.scss";

const PAGE_PATH = "/politika-konfidencialnosti";

export const metadata = buildMetadata(PAGE_PATH);

export default function PrivacyPolicyPage() {
  return (
    <main className={styles.page}>
      <Breadcrumbs
        items={[
          { label: "Главная", href: "/" },
          { label: "Политика конфиденциальности" },
        ]}
      />

      <div className={styles.body}>
        <PrivacyPolicy />
      </div>

      <RequestSection />
    </main>
  );
}
