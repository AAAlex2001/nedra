import { NextResponse, type NextRequest } from "next/server";

const askForPassword = () =>
  new NextResponse("Требуется авторизация", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Admin", charset="UTF-8"' },
  });

const notFound = () => new NextResponse("Not found", { status: 404 });

const isAuthorized = (request: NextRequest) => {
  const header = request.headers.get("authorization");

  if (!header?.startsWith("Basic ")) return false;

  const decoded = atob(header.slice("Basic ".length));
  const separator = decoded.indexOf(":");

  if (separator === -1) return false;

  return (
    decoded.slice(0, separator) === process.env.ADMIN_USER &&
    decoded.slice(separator + 1) === process.env.ADMIN_PASSWORD
  );
};

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const secretPath = process.env.ADMIN_PATH;

  if (pathname.startsWith("/admin")) return notFound();

  if (!secretPath || !pathname.startsWith(`/${secretPath}`)) {
    return NextResponse.next();
  }

  if (!process.env.ADMIN_USER || !process.env.ADMIN_PASSWORD) {
    return new NextResponse("Админка не настроена", { status: 503 });
  }

  if (!isAuthorized(request)) return askForPassword();

  const url = request.nextUrl.clone();
  url.pathname = pathname.replace(`/${secretPath}`, "/admin");

  return NextResponse.rewrite(url);
}

export const config = {
  matcher: "/((?!_next/static|_next/image|favicon.ico).*)",
};
