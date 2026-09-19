import type { Metadata } from "next";
import type { ExpertCatalog } from "@/entities/expert";
import type { Tariff } from "@/entities/tariff";
import { adminBasePath, internalFetch, loadAdmin } from "@/shared/api/server";
import AdminTariffs from "@/widgets/admin/tariffs";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Тарифы",
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

export default async function AdminTariffsPage() {
  const { data, error } = await loadAdmin<Tariff[]>("/v1/tariffs", []);
  const catalog = await loadCatalog();

  return (
    <AdminTariffs catalog={catalog} tariffs={data} error={error} basePath={adminBasePath()} />
  );
}
