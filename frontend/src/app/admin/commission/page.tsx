import type { Metadata } from "next";
import type { CommissionApplicationRecord } from "@/entities/commission";
import type { ExpertCatalog } from "@/entities/expert";
import { adminBasePath, internalFetch, loadAdmin } from "@/shared/api/server";
import AdminCommission from "@/widgets/admin/commission";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Конкурсная комиссия",
};

const loadCatalog = async (): Promise<ExpertCatalog | null> => {
  try {
    const response = await internalFetch("/v1/experts/catalog", { cache: "no-store" });

    if (!response.ok) return null;

    const catalog: ExpertCatalog = await response.json();

    return catalog;
  } catch {
    return null;
  }
};

export default async function AdminCommissionPage() {
  const { data, error } = await loadAdmin<CommissionApplicationRecord[]>(
    "/v1/admin/commission/applications",
    [],
  );
  const catalog = await loadCatalog();

  return (
    <AdminCommission items={data} catalog={catalog} error={error} basePath={adminBasePath()} />
  );
}
