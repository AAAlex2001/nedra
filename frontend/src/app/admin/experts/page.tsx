import type { Metadata } from "next";
import type { ExpertApplicationRecord, ExpertCatalog } from "@/entities/expert";
import { adminBasePath, internalFetch, loadAdmin } from "@/shared/api/server";
import AdminExperts from "@/widgets/admin/experts";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Заявки экспертов",
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

export default async function AdminExpertsPage() {
  const { data, error } = await loadAdmin<ExpertApplicationRecord[]>(
    "/v1/admin/experts/applications",
    [],
  );
  const catalog = await loadCatalog();

  return (
    <AdminExperts items={data} catalog={catalog} error={error} basePath={adminBasePath()} />
  );
}
