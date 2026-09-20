import { NextResponse } from "next/server";
import { parseId, proxyJsonBody, proxyToBackend } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

type RouteContext = {
  params: Promise<{ userId: string }>;
};

export async function PATCH(request: Request, context: RouteContext) {
  const userId = parseId((await context.params).userId);

  if (userId === null) {
    return NextResponse.json({ detail: "Некорректный id" }, { status: 400 });
  }

  return proxyJsonBody(`/v1/admin/experts/${userId}`, "PATCH", request);
}

export async function DELETE(request: Request, context: RouteContext) {
  const userId = parseId((await context.params).userId);

  if (userId === null) {
    return NextResponse.json({ detail: "Некорректный id" }, { status: 400 });
  }

  return proxyToBackend(`/v1/admin/experts/${userId}`, { method: "DELETE" });
}
