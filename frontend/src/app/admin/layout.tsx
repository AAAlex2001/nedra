import type { Metadata } from "next";
import { adminBasePath } from "@/shared/api/server";
import AdminNav from "@/widgets/admin/nav";
import styles from "./layout.module.scss";

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={styles.admin}>
      <AdminNav basePath={adminBasePath()} />

      {children}
    </div>
  );
}
