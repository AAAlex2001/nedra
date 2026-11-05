import { NextResponse } from "next/server";
import { readAdminWorks } from "@/features/expertises-admin/api/read-works";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    return NextResponse.json(await readAdminWorks());
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Бэкенд недоступен";
    return NextResponse.json({ detail }, { status: 502 });
  }
}
