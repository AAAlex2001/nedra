import { NextResponse } from "next/server";
import { parseId, proxyToBackend } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function DELETE(_request: Request, context: RouteContext) {
  const id = parseId((await context.params).id);

  if (id === null) {
    return NextResponse.json({ detail: "Некорректный id" }, { status: 400 });
  }

  return proxyToBackend(`/v1/admin/tags/${id}`, { method: "DELETE" });
}
