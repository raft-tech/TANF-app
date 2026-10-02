import NextLink from "next/link";
import AdminShell from "@/components/admin-shell";
import AdminReadState from "@/components/admin-read-state";
import { adminApi } from "@/lib/admin-api";
import { readAdminResource } from "@/lib/admin-read";
import {
  parseUserQuery,
  userQueryString,
  userDisplayName,
  formatUserDate,
  type SearchParams,
  type AdminUser,
} from "@/lib/admin-users";
import { requireAdminSession } from "@/lib/require-admin-session";

export const dynamic = "force-dynamic";

export default async function UserDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<SearchParams>;
}) {
  const { cookieHeader, requestHeaders, session } = await requireAdminSession();
  const { id } = await params;
  const search = userQueryString(parseUserQuery(await searchParams));
  const result = await readAdminResource<AdminUser>(() =>
    adminApi.users.get(id, {
      cookieHeader,
      incomingHeaders: requestHeaders,
      sourceRoute: `/users/${id}`,
    }),
  );
  return (
    <AdminShell session={session}>
      <NextLink href={`/users${search}`}>Back to user accounts</NextLink>
      {!result.ok ? (
        <>
          <h1>User details</h1>
          <AdminReadState
            title={
              result.status === 404 ? "User not found" : "Could not load user"
            }
            message={
              result.status === 404
                ? "This account does not exist or is no longer available."
                : "Account details are temporarily unavailable. Please try again."
            }
            href={
              result.status === 404
                ? `/users${search}`
                : `/users/${encodeURIComponent(id)}${search}`
            }
            action={
              result.status === 404 ? "Return to user accounts" : "Try again"
            }
          />
        </>
      ) : (
        <>
          <header className="admin-page-header">
            <p className="admin-console__eyebrow">User account</p>
            <h1>{userDisplayName(result.data)}</h1>
            <p>{result.data.email || result.data.username}</p>
          </header>
          <section
            className="admin-dashboard-card"
            aria-label="Account details"
          >
            <h2>Account details</h2>
            <dl className="admin-success__details">
              {Object.entries({
                Username: result.data.username,
                "Approval status": result.data.account_approval_status,
                "Account status": result.data.is_active ? "Active" : "Inactive",
                STT: result.data.stt_name || "Not assigned",
                Roles: result.data.roles.join(", ") || "Not assigned",
                "Date joined (Eastern time)": formatUserDate(
                  result.data.date_joined,
                ),
                "Last login (Eastern time)": formatUserDate(
                  result.data.last_login,
                ),
                "Access requested (Eastern time)": formatUserDate(
                  result.data.access_requested_date,
                ),
              }).map(([label, value]) => (
                <div key={label}>
                  <dt>{label}</dt>
                  <dd>{value}</dd>
                </div>
              ))}
            </dl>
          </section>
          <p>
            <NextLink href={`/users/${result.data.id}/edit`}>
              Edit user account
            </NextLink>
          </p>
        </>
      )}
    </AdminShell>
  );
}
