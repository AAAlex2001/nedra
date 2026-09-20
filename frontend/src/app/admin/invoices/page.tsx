import type { Metadata } from "next";
import type { Invoice } from "@/entities/billing";
import { adminBasePath, loadAdmin } from "@/shared/api/server";
import AdminInvoices from "@/widgets/admin/invoices";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Счета",
};

export default async function AdminInvoicesPage() {
  const { data, error } = await loadAdmin<Invoice[]>("/v1/admin/invoices", []);

  return <AdminInvoices items={data} error={error} basePath={adminBasePath()} />;
}
