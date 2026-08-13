import { GridContainer } from "@trussworks/react-uswds";
import { checkBackendHealth } from "@/lib/admin-auth";
import { requireAdminSession } from "@/lib/admin-page-auth";
import { getBackendHealthSummary } from "@/lib/backend-health-display";
import { getAdminRoleSummary } from "@/lib/admin-session-display";

export default async function AdminHomePage() {
  const { session } = await requireAdminSession();

  const backendHealth = await checkBackendHealth();
  const backendHealthSummary = getBackendHealthSummary(backendHealth);
  const displayName =
    [session.user?.first_name, session.user?.last_name].filter(Boolean).join(" ") ||
    session.user?.email ||
    "Admin user";
  const roles = getAdminRoleSummary(session.user?.roles);
  const sessionStatus = "Authenticated and admin-authorized";
  const statusDetail =
    session.detail ??
    "Django validated your admin session and authorized this view.";
  const acfLogoSrc = "/ACFLogo.svg";

  return (
    <>
        <section className="admin-success" aria-label="Admin login success">
          <GridContainer className="grid-container-widescreen admin-success__shell">
            <div className="admin-success__panel">
              <p className="admin-console__eyebrow">Login successful</p>
              <h1>Welcome to the admin console</h1>
              <p className="admin-success__lede">
                {statusDetail}
              </p>

              <dl className="admin-success__details">
                <div>
                  <dt>User</dt>
                  <dd>{displayName}</dd>
                </div>
                <div>
                  <dt>Email</dt>
                  <dd>{session.user?.email ?? "Not returned"}</dd>
                </div>
                <div>
                  <dt>Roles</dt>
                  <dd>{roles}</dd>
                </div>
                <div>
                  <dt>Session</dt>
                  <dd>{sessionStatus}</dd>
                </div>
                <div>
                  <dt>Backend health</dt>
                  <dd>{backendHealthSummary}</dd>
                </div>
                <div>
                  <dt>Backend URL</dt>
                  <dd>{backendHealth.backendUrl ?? "Not configured"}</dd>
                </div>
              </dl>

              <div className="admin-success__actions">
                <a className="usa-button" href="/users">
                  Manage users
                </a>
                <a className="usa-button usa-button--outline" href="/api-validation">
                  Validate API response
                </a>
                <a className="usa-button usa-button--outline" href="/logout">
                  Sign out
                </a>
              </div>
            </div>
          </GridContainer>
        </section>

        <footer className="usa-footer usa-footer--slim admin-footer">
          <div className="usa-footer__primary-section">
            <div className="grid-container-widescreen grid-row">
              <div className="mobile-lg:grid-col-8">
                <nav className="usa-footer__nav" aria-label="Footer navigation">
                  <ul className="grid-row grid-gap">
                    <li className="mobile-lg:grid-col-6 desktop:grid-col-auto usa-footer__primary-content">
                      <a
                        className="usa-footer__primary-link"
                        href="https://tdp-project-updates.app.cloud.gov/knowledge-center/"
                        target="_blank"
                        rel="noreferrer"
                      >
                        Knowledge Center
                      </a>
                    </li>
                    <li className="mobile-lg:grid-col-6 desktop:grid-col-auto usa-footer__primary-content">
                      <a
                        className="usa-footer__primary-link"
                        href="https://www.acf.hhs.gov/privacy-policy"
                        target="_blank"
                        rel="noreferrer"
                      >
                        Privacy Policy
                      </a>
                    </li>
                    <li className="mobile-lg:grid-col-6 desktop:grid-col-auto usa-footer__primary-content">
                      <a
                        className="usa-footer__primary-link"
                        href="https://www.hhs.gov/vulnerability-disclosure-policy/index.html"
                        target="_blank"
                        rel="noreferrer"
                      >
                        Vulnerability Disclosure Policy
                      </a>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
          <div className="usa-footer__secondary-section">
            <div className="grid-container-widescreen">
              <div className="usa-footer__logo margin-left-neg-205">
                <div className="grid-col-auto">
                  <img
                    src={acfLogoSrc}
                    alt="Administration for Children and Families, Office of Family Assistance"
                    className="mobile-lg:maxw-mobile mobile:width-mobile"
                  />
                </div>
              </div>
            </div>
          </div>
        </footer>
    </>
  );
}
