import { NextResponse } from "next/server";
import { API_INTERNAL_URL } from "@/shared/api/config";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await fetch(`${API_INTERNAL_URL}/v1/requests`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        { detail: `Бэкенд ответил ${response.status}` },
        { status: response.status },
      );
    }

    return NextResponse.json(await response.json());
  } catch {
    return NextResponse.json(
      { detail: "Бэкенд недоступен" },
      { status: 502 },
    );
  }
}
