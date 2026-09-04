import type { Metadata } from "next";
import type { RequestRecord } from "@/entities/request";
import { API_INTERNAL_URL } from "@/shared/api/config";
import AdminRequests from "@/widgets/admin/requests";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Заявки",
  robots: { index: false, follow: false },
};

type LoadResult = {
  items: RequestRecord[];
  error: string | null;
};

const loadRequests = async (): Promise<LoadResult> => {
  try {
    const response = await fetch(`${API_INTERNAL_URL}/v1/requests`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return { items: [], error: `Бэкенд ответил ${response.status}` };
    }

    return { items: (await response.json()) as RequestRecord[], error: null };
  } catch {
    return { items: [], error: "Бэкенд недоступен" };
  }
};

export default async function AdminPage() {
  const { items, error } = await loadRequests();
  const basePath = `/${process.env.ADMIN_PATH ?? ""}`;

  return <AdminRequests items={items} error={error} basePath={basePath} />;
}
