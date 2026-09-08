import { NextResponse } from "next/server";
import { parseId, proxyJsonBody, proxyToBackend } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

type RouteContext = {
  params: Promise<{ id: string }>;
};

const badId = () => NextResponse.json({ detail: "Некорректный id" }, { status: 400 });

export async function GET(_request: Request, context: RouteContext) {
  const id = parseId((await context.params).id);
  if (id === null) return badId();

  return proxyToBackend(`/v1/admin/articles/${id}`);
}

export async function PATCH(request: Request, context: RouteContext) {
  const id = parseId((await context.params).id);
  if (id === null) return badId();

  return proxyJsonBody(`/v1/admin/articles/${id}`, "PATCH", request);
}

export async function DELETE(_request: Request, context: RouteContext) {
  const id = parseId((await context.params).id);
  if (id === null) return badId();

  return proxyToBackend(`/v1/admin/articles/${id}`, { method: "DELETE" });
}
