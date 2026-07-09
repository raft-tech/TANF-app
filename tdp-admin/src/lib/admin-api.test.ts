import { afterEach, describe, expect, it, vi } from "vitest";
import {
  buildAdminApiHeaders,
  fetchDjangoAdminApi,
  getAdminApiUrl,
  isMutatingAdminApiMethod,
  setAuthenticatedNoStore,
} from "./admin-api";

const originalEnv = { ...process.env };

afterEach(() => {
  process.env = { ...originalEnv };
  vi.restoreAllMocks();
});

describe("admin API helper", () => {
  it("builds encoded Django admin API URLs from the configured backend", () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1/";

    expect(getAdminApiUrl(["admin", "users and roles"], "?page=1")).toBe(
      "https://backend.example.gov/v1/admin/users%20and%20roles?page=1"
    );
  });

  it("forwards session, CSRF, request ID, and provenance context", () => {
    const incomingHeaders = new Headers({
      "x-request-id": "request-123",
      "x-forwarded-for": "203.0.113.9",
      "user-agent": "vitest",
      origin: "https://admin.example.gov",
    });

    const headers = buildAdminApiHeaders({
      method: "POST",
      cookieHeader: "sessionid=abc; csrftoken=csrf-cookie",
      incomingHeaders,
      sourceRoute: "/api/admin/test-viewset",
    });

    expect(headers.get("Cookie")).toBe("sessionid=abc; csrftoken=csrf-cookie");
    expect(headers.get("X-CSRFToken")).toBe("csrf-cookie");
    expect(headers.get("x-request-id")).toBe("request-123");
    expect(headers.get("x-forwarded-for")).toBe("203.0.113.9");
    expect(headers.get("user-agent")).toBe("vitest");
    expect(headers.get("origin")).toBe("https://admin.example.gov");
    expect(headers.get("x-service-name")).toBe("tdp-admin");
    expect(headers.get("x-tdp-admin-proxy")).toBe("nextjs");
    expect(headers.get("x-tdp-admin-source-route")).toBe(
      "/api/admin/test-viewset"
    );
  });

  it("does not add CSRF headers for read-only requests", () => {
    const headers = buildAdminApiHeaders({
      method: "GET",
      cookieHeader: "sessionid=abc; csrftoken=csrf-cookie",
    });

    expect(isMutatingAdminApiMethod("GET")).toBe(false);
    expect(headers.get("X-CSRFToken")).toBeNull();
    expect(headers.get("x-request-id")).toBeTruthy();
  });

  it("defaults authenticated response cache headers to no-store", () => {
    const headers = setAuthenticatedNoStore(new Headers({ "x-test": "ok" }));

    expect(headers.get("Cache-Control")).toBe("no-store");
    expect(headers.get("Pragma")).toBe("no-cache");
    expect(headers.get("Expires")).toBe("0");
    expect(headers.get("x-test")).toBe("ok");
  });

  it("fetches Django with no-store and no business logic shaping", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        Response.json({ results: [{ id: 1, status: "from Django" }] })
      )
    );

    const response = await fetchDjangoAdminApi(["test-viewset"], {
      search: "?page=1",
      context: {
        method: "GET",
        cookieHeader: "sessionid=abc",
        sourceRoute: "/api-validation",
      },
    });

    expect(await response.json()).toEqual({
      results: [{ id: 1, status: "from Django" }],
    });
    expect(fetch).toHaveBeenCalledWith(
      "https://backend.example.gov/v1/test-viewset?page=1",
      expect.objectContaining({
        method: "GET",
        credentials: "include",
        cache: "no-store",
      })
    );
  });
});
