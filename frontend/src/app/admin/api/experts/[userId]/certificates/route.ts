import { NextResponse } from "next/server";
import { parseId, proxyJsonBody } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

type RouteContext = {
  params: Promise<{ userId: string }>;
};

export async function POST(request: Request, context: RouteContext) {
  const params = await context.params;
  const userId = parseId(params.userId);

  if (userId === null) {
    return NextResponse.json({ detail: "Некорректный id" }, { status: 400 });
  }

  return proxyJsonBody(`/v1/admin/experts/${userId}/certificates`, "POST", request);
}
