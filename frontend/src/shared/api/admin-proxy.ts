import { NextResponse } from "next/server";
import { adminFetch } from "./server";

export const proxyToBackend = async (path: string, init?: RequestInit) => {
  try {
    const response = await adminFetch(path, init);

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    const body = await response.text();

    return new NextResponse(body, {
      status: response.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return NextResponse.json({ detail: "Бэкенд недоступен" }, { status: 502 });
  }
};

export const proxyJsonBody = async (path: string, method: string, request: Request) =>
  proxyToBackend(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: await request.text(),
  });

export const proxyFile = async (path: string) => {
  try {
    const response = await adminFetch(path);

    if (!response.ok) {
      const body = await response.text();

      return new NextResponse(body, {
        status: response.status,
        headers: { "Content-Type": "application/json" },
      });
    }

    const headers = new Headers();
    const contentType = response.headers.get("content-type");
    const disposition = response.headers.get("content-disposition");
    if (contentType) headers.set("Content-Type", contentType);
    if (disposition) headers.set("Content-Disposition", disposition);

    return new NextResponse(response.body, { status: 200, headers });
  } catch {
    return NextResponse.json({ detail: "Бэкенд недоступен" }, { status: 502 });
  }
};

export const parseId = (value: string): number | null => {
  const id = Number(value);
  return Number.isInteger(id) && id > 0 ? id : null;
};
