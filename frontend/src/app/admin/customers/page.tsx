import type { Metadata } from "next";
import type { CustomerRecord } from "@/entities/user";
import { loadAdmin } from "@/shared/api/server";
import AdminCustomers from "@/widgets/admin/customers";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Заказчики",
};

export default async function AdminCustomersPage() {
  const { data, error } = await loadAdmin<CustomerRecord[]>("/v1/admin/customers", []);

  return <AdminCustomers items={data} error={error} />;
}
