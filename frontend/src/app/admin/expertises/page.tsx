import type { Metadata } from "next";
import type { ExpertCatalog } from "@/entities/expert";
import type { ExpertiseAdminRecord, ExpertOption } from "@/features/expertises-admin";
import { adminBasePath, internalFetch, loadAdmin } from "@/shared/api/server";
import AdminExpertises from "@/widgets/admin/expertises";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Заявки на экспертизу",
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

export default async function AdminExpertisesPage() {
  const { data, error } = await loadAdmin<ExpertiseAdminRecord[]>("/v1/admin/expertises", []);
  const catalog = await loadCatalog();
  const experts = await loadAdmin<ExpertOption[]>("/v1/admin/experts", []);

  return (
    <AdminExpertises
      items={data}
      catalog={catalog}
      experts={experts.data}
      error={error}
      basePath={adminBasePath()}
    />
  );
}
