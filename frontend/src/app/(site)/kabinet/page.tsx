import { notFound } from "next/navigation";
// import type { Metadata } from "next";
// import { hasSessionCookie } from "@/entities/user/api/session-server";
// import Breadcrumbs from "@/shared/ui/breadcrumbs";
// import SectionHeading from "@/shared/ui/section-heading";
// import Cabinet from "@/widgets/cabinet";
// import styles from "./page.module.scss";

// export const metadata: Metadata = {
//   title: "Личный кабинет",
//   robots: { index: false, follow: false },
// };

export default async function CabinetPage() {
  notFound();

  // const guest = !(await hasSessionCookie());
  //
  // return (
  //   <main className={styles.page}>
  //     <Breadcrumbs
  //       items={[
  //         { label: "Главная", href: "/" },
  //         { label: "Личный кабинет" },
  //       ]}
  //     />
  //
  //     <div className={`${styles.body} ${guest ? styles.bodyGuest : ""}`}>
  //       <SectionHeading title="Личный кабинет" />
  //       <Cabinet />
  //     </div>
  //   </main>
  // );
}
