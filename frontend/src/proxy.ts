import { NextResponse, type NextRequest } from "next/server";

const askForPassword = () =>
  new NextResponse("Требуется авторизация", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Admin", charset="UTF-8"' },
  });

export function proxy(request: NextRequest) {
  const user = process.env.ADMIN_USER;
  const password = process.env.ADMIN_PASSWORD;

  if (!user || !password) {
    return new NextResponse("Админка не настроена", { status: 503 });
  }

  const header = request.headers.get("authorization");

  if (!header?.startsWith("Basic ")) return askForPassword();

  const decoded = atob(header.slice("Basic ".length));
  const separator = decoded.indexOf(":");

  if (separator === -1) return askForPassword();

  const isValid =
    decoded.slice(0, separator) === user &&
    decoded.slice(separator + 1) === password;

  return isValid ? NextResponse.next() : askForPassword();
}

export const config = {
  matcher: "/admin/:path*",
};
