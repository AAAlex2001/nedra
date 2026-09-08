import { proxyToBackend } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const form = await request.formData();

  return proxyToBackend("/v1/admin/uploads", { method: "POST", body: form });
}
