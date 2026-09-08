import { proxyToBackend } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

export async function GET() {
  return proxyToBackend("/v1/requests");
}
