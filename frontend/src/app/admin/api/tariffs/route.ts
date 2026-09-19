import { proxyJsonBody, proxyToBackend } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

export async function GET() {
  return proxyToBackend("/v1/tariffs");
}

export async function PUT(request: Request) {
  return proxyJsonBody("/v1/admin/tariffs", "PUT", request);
}
