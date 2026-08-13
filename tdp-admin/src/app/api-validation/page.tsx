import { GridContainer } from "@trussworks/react-uswds";
import NextLink from "next/link";
import { requestAdminApi, setAuthenticatedNoStore } from "@/lib/admin-api";
import {
  requireAdminSession,
  type RequiredAdminSessionContext,
} from "@/lib/admin-page-auth";

export const dynamic = "force-dynamic";

function toPathSegments(endpoint: string) {
  return endpoint
    .split("/")
    .map((segment) => segment.trim())
    .filter(Boolean);
}

async function fetchValidationResponse({
  endpoint,
  cookieHeader,
  incomingHeaders,
}: {
  endpoint: string;
  cookieHeader: string | null;
  incomingHeaders: RequiredAdminSessionContext["requestHeaders"];
}) {
  const response = await requestAdminApi(toPathSegments(endpoint), {
    method: "GET",
    cookieHeader,
    incomingHeaders,
    sourceRoute: "/api-validation",
  });
  const body = await response.text();

  return {
    status: response.status,
    statusText: response.statusText,
    cacheControl: setAuthenticatedNoStore(new Headers(response.headers)).get(
      "Cache-Control"
    ),
    contentType: response.headers.get("content-type") ?? "Not returned",
    body,
  };
}

export default async function ApiValidationPage({
  searchParams,
}: {
  searchParams: Promise<{ endpoint?: string }>;
}) {
  const { cookieHeader, requestHeaders } = await requireAdminSession();

  const params = await searchParams;
  const endpoint = params.endpoint ?? "auth_check";
  const validation = await fetchValidationResponse({
    endpoint,
    cookieHeader,
    incomingHeaders: requestHeaders,
  }).catch((err) => ({
    status: 500,
    statusText: "Validation request failed",
    cacheControl: "no-store",
    contentType: "Not returned",
    body: err instanceof Error ? err.message : String(err),
  }));

  return (
    <section className="admin-success" aria-label="API response validation">
      <GridContainer className="grid-container-widescreen admin-success__shell">
        <div className="admin-success__panel">
          <p className="admin-console__eyebrow">API validation</p>
          <h1>Django API response validation</h1>
          <p className="admin-success__lede">
            This page calls one Django endpoint through the shared admin API helper and
            displays the response returned by Django.
          </p>

          <div className="admin-success__actions">
            <NextLink className="usa-button usa-button--outline" href="/">
              Return to main page
            </NextLink>
          </div>

          <dl className="admin-success__details">
            <div>
              <dt>Endpoint</dt>
              <dd>{endpoint}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>
                {validation.status} {validation.statusText}
              </dd>
            </div>
            <div>
              <dt>Cache-Control</dt>
              <dd>{validation.cacheControl}</dd>
            </div>
            <div>
              <dt>Content-Type</dt>
              <dd>{validation.contentType}</dd>
            </div>
          </dl>

          <pre className="admin-api-validation__body">{validation.body}</pre>
        </div>
      </GridContainer>
    </section>
  );
}
