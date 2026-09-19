import { NextResponse } from "next/server";
import { parseId, proxyJsonBody } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function POST(request: Request, context: RouteContext) {
  const id = parseId((await context.params).id);

  if (id === null) {
    return NextResponse.json({ detail: "Некорректный id" }, { status: 400 });
  }

  return proxyJsonBody(`/v1/admin/experts/applications/${id}/reject`, "POST", request);
}
