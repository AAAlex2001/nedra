import type { Metadata } from "next";
import type { RequestRecord } from "@/entities/request";
import { adminBasePath, loadAdmin } from "@/shared/api/server";
import AdminRequests from "@/widgets/admin/requests";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Заявки",
};

export default async function AdminPage() {
  const { data, error } = await loadAdmin<RequestRecord[]>("/v1/requests", []);

  return <AdminRequests items={data} error={error} basePath={adminBasePath()} />;
}
