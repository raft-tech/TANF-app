import { afterEach, describe, expect, it, vi } from "vitest";
import {
  checkBackendHealth,
  buildAdminRequestHeaders,
  checkAdminSession,
  getAdminAuthBaseUrl,
  getAdminAuthCheckUrl,
  getAdminLoginUrl,
  getAdminLogoutUrl,
  getAuthBaseUrl,
  getBackendBaseUrl,
  getBrowserAuthBaseUrl,
  getCsrfTokenFromCookie,
  getLoginUrl,
  getProviderLoginPath,
} from "./admin-auth";

const originalEnv = { ...process.env };

afterEach(() => {
  process.env = { ...originalEnv };
  vi.restoreAllMocks();
});

describe("admin auth helpers", () => {
  it("prefers the explicit auth URL over the backend URL", () => {
    process.env.NEXT_PUBLIC_AUTH_URL = "https://auth.example.gov/";
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1";

    expect(getBackendBaseUrl()).toBe("https://backend.example.gov/v1");
    expect(getAuthBaseUrl()).toBe("https://auth.example.gov");
    expect(getLoginUrl("dotgov")).toBe("https://auth.example.gov/login/dotgov");
    expect(getLoginUrl("ams")).toBe("https://auth.example.gov/login/ams");
    expect(getAdminAuthBaseUrl()).toBe("https://auth.example.gov/admin-auth");
    expect(getAdminLoginUrl("ams", "https://admin.example.gov/")).toBe(
      "https://auth.example.gov/admin-auth/login/ams?next=https%3A%2F%2Fadmin.example.gov%2F"
    );
    expect(getAdminAuthCheckUrl()).toBe("https://auth.example.gov/admin-auth/auth_check");
    expect(getAdminLogoutUrl()).toBe("https://auth.example.gov/admin-auth/logout/oidc");
    expect(getProviderLoginPath("dotgov")).toBe("/login/dotgov");
  });

  it("uses a browser-reachable auth URL for redirects when configured", () => {
    process.env.NEXT_PUBLIC_AUTH_URL = "http://host.docker.internal:8989";
    process.env.NEXT_PUBLIC_AUTH_BROWSER_URL = "http://localhost:8989";

    expect(getAuthBaseUrl()).toBe("http://host.docker.internal:8989");
    expect(getBrowserAuthBaseUrl()).toBe("http://localhost:8989");
    expect(getAdminLoginUrl("dotgov")).toBe(
      "http://localhost:8989/admin-auth/login/dotgov"
    );
    expect(getAdminLogoutUrl()).toBe(
      "http://localhost:8989/admin-auth/logout/oidc"
    );
  });

  it("derives the auth base from the backend URL when needed", () => {
    delete process.env.NEXT_PUBLIC_AUTH_URL;
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1/";

    expect(getAuthBaseUrl()).toBe("https://backend.example.gov");
    expect(getLoginUrl("dotgov")).toBe("https://backend.example.gov/login/dotgov");
  });

  it("returns a failed backend health result for non-OK responses", async () => {
    process.env.NEXT_PUBLIC_BACKEND_URL = "https://backend.example.gov/v1/";
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("missing", { status: 404, statusText: "Not Found" }))
    );

    const result = await checkBackendHealth();

    expect(result.ok).toBe(false);
    expect(result.backendUrl).toBe("https://backend.example.gov/v1");
    expect(result.authCheckUrl).toBe("https://backend.example.gov/v1/auth_check");
    expect(result.status).toBe(404);
    expect(result.error).toContain("404");
  });

  it("extracts and forwards Django CSRF context for mutating requests", () => {
    const cookieHeader = "sessionid=abc; csrftoken=my-csrf-token";
    const headers = buildAdminRequestHeaders({
      cookieHeader,
      includeCsrf: true,
    });

    expect(getCsrfTokenFromCookie(cookieHeader)).toBe("my-csrf-token");
    expect(headers.get("Cookie")).toBe(cookieHeader);
    expect(headers.get("X-CSRFToken")).toBe("my-csrf-token");
    expect(headers.get("x-service-name")).toBe("tdp-admin");
  });

  it("checks the admin-scoped Django session", async () => {
    process.env.NEXT_PUBLIC_AUTH_URL = "https://auth.example.gov";
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        Response.json({
          authenticated: true,
          authorized: true,
          csrf: "csrf-token",
          user: { email: "admin@example.gov" },
        })
      )
    );

    const result = await checkAdminSession("sessionid=abc");

    expect(result.authenticated).toBe(true);
    expect(result.authorized).toBe(true);
    expect(result.csrf).toBe("csrf-token");
    expect(fetch).toHaveBeenCalledWith(
      "https://auth.example.gov/admin-auth/auth_check",
      expect.objectContaining({
        method: "GET",
        credentials: "include",
        cache: "no-store",
      })
    );
  });
});
