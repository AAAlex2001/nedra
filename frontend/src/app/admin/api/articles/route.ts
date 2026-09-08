import { proxyJsonBody, proxyToBackend } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

export async function GET() {
  return proxyToBackend("/v1/admin/articles");
}

export async function POST(request: Request) {
  return proxyJsonBody("/v1/admin/articles", "POST", request);
}
