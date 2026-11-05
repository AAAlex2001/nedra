import { NextResponse } from "next/server";
import { parseId, proxyToBackend } from "@/shared/api/admin-proxy";

export const dynamic = "force-dynamic";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function PATCH(request: Request, context: RouteContext) {
  const id = parseId((await context.params).id);

  if (id === null) {
    return NextResponse.json({ detail: "Некорректный id" }, { status: 400 });
  }

  const payload = await request.json();
  const service = payload.service;

  if (service !== "audit" && service !== "expertise") {
    return NextResponse.json({ detail: "Укажите вид заявки" }, { status: 400 });
  }

  const { service: ignoredService, ...changes } = payload;
  void ignoredService;

  return proxyToBackend(`/v1/admin/${service === "audit" ? "audits" : "expertises"}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(changes),
  });
}

export async function DELETE(request: Request, context: RouteContext) {
  const id = parseId((await context.params).id);

  if (id === null) {
    return NextResponse.json({ detail: "Некорректный id" }, { status: 400 });
  }

  const service = new URL(request.url).searchParams.get("service");

  if (service !== "audit" && service !== "expertise") {
    return NextResponse.json({ detail: "Укажите вид заявки" }, { status: 400 });
  }

  return proxyToBackend(`/v1/admin/${service === "audit" ? "audits" : "expertises"}/${id}`, { method: "DELETE" });
}
