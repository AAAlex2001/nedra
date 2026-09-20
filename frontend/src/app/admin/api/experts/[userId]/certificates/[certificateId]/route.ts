import { NextResponse } from "next/server";
import { parseId, proxyJsonBody, proxyToBackend } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

type RouteContext = {
  params: Promise<{ userId: string; certificateId: string }>;
};

const readIds = async (context: RouteContext) => {
  const params = await context.params;

  return { userId: parseId(params.userId), certificateId: parseId(params.certificateId) };
};

export async function PATCH(request: Request, context: RouteContext) {
  const { userId, certificateId } = await readIds(context);

  if (userId === null || certificateId === null) {
    return NextResponse.json({ detail: "Некорректный id" }, { status: 400 });
  }

  return proxyJsonBody(
    `/v1/admin/experts/${userId}/certificates/${certificateId}`,
    "PATCH",
    request,
  );
}

export async function DELETE(request: Request, context: RouteContext) {
  const { userId, certificateId } = await readIds(context);

  if (userId === null || certificateId === null) {
    return NextResponse.json({ detail: "Некорректный id" }, { status: 400 });
  }

  return proxyToBackend(`/v1/admin/experts/${userId}/certificates/${certificateId}`, {
    method: "DELETE",
  });
}
