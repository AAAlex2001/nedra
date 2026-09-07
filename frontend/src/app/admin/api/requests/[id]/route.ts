import { NextResponse } from "next/server";
import { API_INTERNAL_URL } from "@/shared/api/config";

export const dynamic = "force-dynamic";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function DELETE(_request: Request, context: RouteContext) {
  const { id } = await context.params;
  const requestId = Number(id);

  if (!Number.isInteger(requestId) || requestId <= 0) {
    return NextResponse.json({ detail: "Некорректный id" }, { status: 400 });
  }

  try {
    const response = await fetch(`${API_INTERNAL_URL}/v1/request/${requestId}`, {
      method: "DELETE",
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        { detail: `Бэкенд ответил ${response.status}` },
        { status: response.status },
      );
    }

    return new NextResponse(null, { status: 204 });
  } catch {
    return NextResponse.json({ detail: "Бэкенд недоступен" }, { status: 502 });
  }
}
