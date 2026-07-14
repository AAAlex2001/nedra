import type { ReactNode } from "react";
import Breadcrumbs from "@/shared/ui/breadcrumbs";
import SvedeniyaNav from "@/shared/ui/svedeniya-nav";
import styles from "./style.module.scss";

type SvedeniyaPageProps = {
  activeSlug: string;
  crumb: string;
  children: ReactNode;
};

const SvedeniyaPage = ({ activeSlug, crumb, children }: SvedeniyaPageProps) => (
  <main className={styles.page}>
    <Breadcrumbs
      items={[
        { label: "Главная", href: "/" },
        {
          label: "Сведения об образовательной организации",
          href: "/svedeniya",
        },
        { label: crumb },
      ]}
    />

    <div className={styles.sidebar}>
      <SvedeniyaNav activeSlug={activeSlug} />
    </div>

    <div className={styles.body}>{children}</div>
  </main>
);

export default SvedeniyaPage;
