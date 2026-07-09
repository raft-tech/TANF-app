import { NextRequest, NextResponse } from "next/server";
import {
  buildAdminApiHeaders,
  fetchDjangoAdminApi,
  setAuthenticatedNoStore,
} from "@/lib/admin-api";

async function proxyAdminRequest(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const { path } = await context.params;
  const cookieHeader = request.headers.get("cookie");
  const csrfToken = request.headers.get("X-CSRFToken");
  const requestHeaders = buildAdminApiHeaders({
    method: request.method,
    cookieHeader,
    csrfToken,
    incomingHeaders: request.headers,
    sourceRoute: request.nextUrl.pathname,
  });
  const contentType = request.headers.get("content-type");

  if (contentType) {
    requestHeaders.set("content-type", contentType);
  }

  let response: Response;

  try {
    response = await fetchDjangoAdminApi(path, {
      search: request.nextUrl.search,
      body:
        request.method === "GET" || request.method === "HEAD"
          ? undefined
          : await request.text(),
      headers: requestHeaders,
      context: { method: request.method },
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      {
        ok: false,
        error: message,
      },
      {
        status: 500,
        headers: setAuthenticatedNoStore(new Headers()),
      }
    );
  }

  const responseHeaders = setAuthenticatedNoStore(new Headers(response.headers));

  return new NextResponse(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
}

export const GET = proxyAdminRequest;
export const POST = proxyAdminRequest;
export const PUT = proxyAdminRequest;
export const PATCH = proxyAdminRequest;
export const DELETE = proxyAdminRequest;
