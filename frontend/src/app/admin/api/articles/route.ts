import { proxyJsonBody, proxyToBackend } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const { search } = new URL(request.url);

  return proxyToBackend(`/v1/admin/articles${search}`);
}

export async function POST(request: Request) {
  return proxyJsonBody("/v1/admin/articles", "POST", request);
}
