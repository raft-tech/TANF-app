import { headers } from "next/headers";
import { forbidden, notFound, redirect } from "next/navigation";
import { GridContainer } from "@trussworks/react-uswds";
import NextLink from "next/link";
import { UserAdminForm } from "@/components/user-admin-form";
import { adminApi } from "@/lib/admin-api";
import { checkAdminSession } from "@/lib/admin-auth";
import type { AdminFormMetadata } from "@/lib/admin-form";

export const dynamic = "force-dynamic";

export default async function UserEditPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const requestHeaders = await headers();
  const cookieHeader = requestHeaders.get("cookie");
  const session = await checkAdminSession(cookieHeader);

  if (!session.authenticated) {
    redirect("/login");
  }

  if (session.authorized !== true) {
    forbidden();
  }

  const { id } = await params;
  const response = await adminApi.users.formMetadata(id, {
    cookieHeader,
    incomingHeaders: requestHeaders,
    sourceRoute: `/users/${id}/edit`,
  });

  if (response.status === 404) {
    notFound();
  }

  const metadata = (await response
    .json()
    .catch(() => null)) as AdminFormMetadata | null;

  return (
    <main className="admin-login-page" id="main-content">
      <section className="admin-gov-banner" aria-label="Official government website">
        <div className="grid-container-widescreen admin-gov-banner__inner">
          <p>A Demo website of the United States government</p>
          <p>Here&apos;s how you know</p>
        </div>
      </section>

      <header className="usa-header usa-header--extended admin-header">
        <div className="grid-container-widescreen usa-nav__wide desktop:padding-left-4 desktop:border-bottom-0 mobile:border-bottom-1px mobile:padding-left-0 mobile:padding-right-0">
          <div className="usa-logo" id="extended-logo">
            <em className="usa-logo__text">
              <NextLink href="/" aria-label="TANF Data Portal Admin Home">
                TANF Data Portal Admin
              </NextLink>
            </em>
          </div>
        </div>
      </header>

      <section className="admin-success" aria-label="Edit user">
        <GridContainer className="grid-container-widescreen admin-success__shell">
          <div className="admin-success__panel admin-success__panel--form">
            <p className="admin-console__eyebrow">Users</p>
            <h1>{metadata?.object.label ?? "Edit user"}</h1>

            {!response.ok || !metadata ? (
              <div
                className="usa-alert usa-alert--error admin-form__alert"
                role="alert"
              >
                <div className="usa-alert__body">
                  <h2 className="usa-alert__heading">Could not load user form</h2>
                </div>
              </div>
            ) : (
              <UserAdminForm metadata={metadata} csrfToken={session.csrf ?? null} />
            )}
          </div>
        </GridContainer>
      </section>
    </main>
  );
}
