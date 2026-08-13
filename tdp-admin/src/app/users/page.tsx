import { GridContainer } from "@trussworks/react-uswds";
import NextLink from "next/link";
import { adminApi } from "@/lib/admin-api";
import { requireAdminSession } from "@/lib/admin-page-auth";

export const dynamic = "force-dynamic";

type AdminUser = {
  id: string;
  username: string;
  first_name?: string;
  last_name?: string;
  account_approval_status?: string;
  stt?: string | number | null;
};

type UserListResponse = AdminUser[] | { results?: AdminUser[] };

function usersFromResponse(data: UserListResponse) {
  return Array.isArray(data) ? data : data.results ?? [];
}

export default async function UsersPage() {
  const { cookieHeader, requestHeaders } = await requireAdminSession();

  const response = await adminApi.users.list({
    cookieHeader,
    incomingHeaders: requestHeaders,
    sourceRoute: "/users",
  });
  const data = (await response.json().catch(() => [])) as UserListResponse;
  const users = response.ok ? usersFromResponse(data) : [];

  return (
    <section className="admin-success" aria-label="Users">
      <GridContainer className="grid-container-widescreen admin-success__shell">
        <div className="admin-success__panel admin-success__panel--wide">
          <p className="admin-console__eyebrow">Users</p>
          <h1>User accounts</h1>

          <div className="admin-success__actions">
            <NextLink className="usa-button usa-button--outline" href="/">
              Return to main page
            </NextLink>
          </div>

          {!response.ok && (
            <div
              className="usa-alert usa-alert--error admin-form__alert"
              role="alert"
            >
              <div className="usa-alert__body">
                <h2 className="usa-alert__heading">Could not load users</h2>
              </div>
            </div>
          )}

          {users.length > 0 && (
            <div className="admin-table-wrap">
              <table className="usa-table usa-table--borderless admin-table">
                <thead>
                  <tr>
                    <th scope="col">User</th>
                    <th scope="col">Status</th>
                    <th scope="col">STT</th>
                    <th scope="col">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => {
                    const displayName =
                      [user.first_name, user.last_name]
                        .filter(Boolean)
                        .join(" ") || user.username;

                    return (
                      <tr key={user.id}>
                        <th scope="row">
                          <span className="admin-table__primary">
                            {displayName}
                          </span>
                          <span className="admin-table__secondary">
                            {user.username}
                          </span>
                        </th>
                        <td>{user.account_approval_status ?? ""}</td>
                        <td>{user.stt ?? ""}</td>
                        <td>
                          <NextLink
                            className="usa-button usa-button--outline admin-table__action"
                            href={`/users/${user.id}/edit`}
                          >
                            Edit
                          </NextLink>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </GridContainer>
    </section>
  );
}
