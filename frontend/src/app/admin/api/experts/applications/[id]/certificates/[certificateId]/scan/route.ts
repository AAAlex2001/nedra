import { NextResponse } from "next/server";
import { parseId, proxyFile } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

type RouteContext = {
  params: Promise<{ id: string; certificateId: string }>;
};

export async function GET(request: Request, context: RouteContext) {
  const params = await context.params;
  const id = parseId(params.id);
  const certificateId = parseId(params.certificateId);

  if (id === null || certificateId === null) {
    return NextResponse.json({ detail: "Некорректный id" }, { status: 400 });
  }

  return proxyFile(`/v1/admin/experts/applications/${id}/certificates/${certificateId}/scan`);
}
