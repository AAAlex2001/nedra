import { readAdminWorks } from "@/features/expertises-admin/api/read-works";
import type { Metadata } from "next";
import type { ExpertCatalog } from "@/entities/expert";
import type { ExpertiseAdminRecord, ExpertOption } from "@/features/expertises-admin";
import { adminBasePath, internalFetch, loadAdmin } from "@/shared/api/server";
import AdminExpertises from "@/widgets/admin/expertises";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Экспертизы и аудиты",
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
  let data: ExpertiseAdminRecord[] = [];
  let error: string | null = null;

  try {
    data = await readAdminWorks();
  } catch (caught) {
    error = caught instanceof Error ? caught.message : "Не удалось загрузить заявки";
  }
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
