"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMemo, useState } from "react";
import {
  ADMIN_DASHBOARD_NAV_ITEMS,
  ADMIN_PRIMARY_NAV_ITEMS,
  getDefaultExpandedAdminNavIds,
  getAdminNavigationTitle,
  getVisibleAdminNavItems,
  isAdminNavItemActive,
  type AdminNavIconName,
  type AdminNavItem,
  type AdminRoleValue,
} from "@/lib/admin-navigation";

function NavIcon({ name }: { name?: AdminNavIconName }) {
  if (!name) {
    return null;
  }

  return (
    <svg
      className="admin-sidenav__icon"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.8"
    >
      {getIconPath(name)}
    </svg>
  );
}

function getIconPath(name: AdminNavIconName) {
  switch (name) {
    case "appearance":
      return (
        <>
          <path d="M12 3a9 9 0 1 0 0 18h1.25a1.75 1.75 0 0 0 .4-3.45l-.9-.2a1.3 1.3 0 0 1 .3-2.57H15a6 6 0 0 0 0-12h-3Z" />
          <path d="M7.7 10.4h.1M9.9 7.4h.1M13.2 7.1h.1M16 9.4h.1" />
        </>
      );
    case "approval":
      return (
        <>
          <path d="M6 4h9l3 3v13H6z" />
          <path d="M14 4v4h4M9 14l2 2 4-5" />
        </>
      );
    case "collapse":
      return (
        <>
          <path d="M4 5h16v14H4zM9 5v14" />
          <path d="m15 9-3 3 3 3" />
        </>
      );
    case "dashboard":
      return (
        <>
          <path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z" />
        </>
      );
    case "data-files":
      return (
        <>
          <path d="M3.5 6.5h6l1.75 2H20.5v9.5a1.5 1.5 0 0 1-1.5 1.5H5a1.5 1.5 0 0 1-1.5-1.5z" />
          <path d="M3.5 8.5V6A1.5 1.5 0 0 1 5 4.5h4.25l1.75 2" />
        </>
      );
    case "etl":
      return (
        <>
          <path d="M4 7h10M10 3l4 4-4 4" />
          <path d="M20 17H10M14 13l-4 4 4 4" />
        </>
      );
    case "feature-flags":
      return (
        <>
          <path d="M6 20V4" />
          <path d="M6 5h11l-1.5 3L17 11H6" />
        </>
      );
    case "feedback":
      return (
        <>
          <path d="M5 5h14v10H9l-4 4z" />
          <path d="M8.5 8.5h7M8.5 11.5h4" />
        </>
      );
    case "home":
      return (
        <>
          <path d="m3 10.5 9-7 9 7" />
          <path d="M5.5 9.5V20h13V9.5" />
          <path d="M9.5 20v-6h5v6" />
        </>
      );
    case "log-entries":
      return (
        <>
          <path d="M6 4h9l3 3v13H6z" />
          <path d="M14.5 4v4h3.5M9 12h6M9 15h6M9 18h3" />
        </>
      );
    case "parsers":
      return (
        <>
          <path d="M8 5 4 12l4 7M16 5l4 7-4 7" />
          <path d="m13.5 6.5-3 11" />
        </>
      );
    case "periodic-tasks":
      return (
        <>
          <path d="M6 5h12a2 2 0 0 1 2 2v11H4V7a2 2 0 0 1 2-2Z" />
          <path d="M8 3v4M16 3v4M4 10h16M8 15l2 2 4-4" />
        </>
      );
    case "reports":
      return (
        <>
          <path d="M5 20V4h14v16z" />
          <path d="M9 16v-4M12 16V8M15 16v-6" />
        </>
      );
    case "search":
      return (
        <>
          <path d="M11 18a7 7 0 1 1 0-14 7 7 0 0 1 0 14Z" />
          <path d="m16.5 16.5 3.5 3.5" />
        </>
      );
    case "search-indexes":
      return (
        <>
          <path d="M5 4h8l4 4v5" />
          <path d="M13 4v5h4M7.5 12h4" />
          <path d="M13.5 17.5a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0Z" />
          <path d="m19.5 20.5 1.5 1.5" />
        </>
      );
    case "security":
      return (
        <>
          <path d="M12 3 5 6v5c0 4.25 2.75 7.5 7 10 4.25-2.5 7-5.75 7-10V6z" />
          <path d="m9 12 2 2 4-5" />
        </>
      );
    case "stts":
      return (
        <>
          <circle cx="6.5" cy="7" r="2.5" />
          <circle cx="17.5" cy="7" r="2.5" />
          <circle cx="12" cy="17" r="2.5" />
          <path d="m8 9 2.75 5M16 9l-2.75 5M9 17h-1" />
        </>
      );
    case "users":
      return (
        <>
          <path d="M8.5 11a3.25 3.25 0 1 0 0-6.5 3.25 3.25 0 0 0 0 6.5Z" />
          <path d="M3.5 20a5 5 0 0 1 10 0" />
          <path d="M16 10.5a2.75 2.75 0 1 0 0-5.5" />
          <path d="M16 14.5a4 4 0 0 1 4 4" />
        </>
      );
  }
}

function navItemMatchesSearch(item: AdminNavItem, query: string) {
  return item.label.toLowerCase().includes(query);
}

function filterNavItemsBySearch(
  items: readonly AdminNavItem[],
  searchQuery: string
) {
  const query = searchQuery.trim().toLowerCase();

  if (!query) {
    return [...items];
  }

  return items.reduce<AdminNavItem[]>((filteredItems, item) => {
    const childMatches = item.children
      ? filterNavItemsBySearch(item.children, query)
      : [];

    if (navItemMatchesSearch(item, query)) {
      filteredItems.push(item);
    } else if (childMatches.length) {
      filteredItems.push({ ...item, children: childMatches });
    }

    return filteredItems;
  }, []);
}

function NavLink({
  item,
  currentPath,
}: {
  item: AdminNavItem;
  currentPath: string;
}) {
  const linkContent = (
    <>
      <NavIcon name={item.icon} />
      <span className="admin-sidenav__label">{item.label}</span>
    </>
  );

  const isActive = isAdminNavItemActive(currentPath, item);

  if (!item.href || item.disabled) {
    return (
      <span
        className="admin-sidenav__link admin-sidenav__link--disabled"
        aria-disabled="true"
        title="Page not available yet"
      >
        {linkContent}
      </span>
    );
  }

  return (
    <Link
      className="admin-sidenav__link"
      href={item.href}
      aria-current={isActive ? "page" : undefined}
    >
      {linkContent}
    </Link>
  );
}

function NavGroup({
  item,
  currentPath,
  expanded,
  onToggle,
}: {
  item: AdminNavItem;
  currentPath: string;
  expanded: boolean;
  onToggle: () => void;
}) {
  const groupId = `admin-nav-group-${item.id}`;
  const isActive = isAdminNavItemActive(currentPath, item);

  return (
    <div className="admin-sidenav__group">
      <button
        className="admin-sidenav__group-button"
        type="button"
        aria-expanded={expanded}
        aria-controls={groupId}
        data-active={isActive ? "true" : undefined}
        onClick={onToggle}
      >
        <NavIcon name={item.icon} />
        <span className="admin-sidenav__label">{item.label}</span>
        <span className="admin-sidenav__chevron" aria-hidden="true" />
      </button>
      <ul className="admin-sidenav__children" id={groupId} hidden={!expanded}>
        {item.children?.map((child) => (
          <li key={child.id}>
            <NavLink item={child} currentPath={currentPath} />
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function AdminNavigation({
  roles,
}: {
  roles?: readonly AdminRoleValue[] | null;
}) {
  const currentPath = usePathname() || "/";
  const navigationTitle = useMemo(() => getAdminNavigationTitle(roles), [roles]);
  const primaryItems = useMemo(
    () => getVisibleAdminNavItems(roles, ADMIN_PRIMARY_NAV_ITEMS),
    [roles]
  );
  const dashboardItems = useMemo(
    () => getVisibleAdminNavItems(roles, ADMIN_DASHBOARD_NAV_ITEMS),
    [roles]
  );
  const defaultExpandedIds = useMemo(
    () => getDefaultExpandedAdminNavIds(currentPath, primaryItems),
    [currentPath, primaryItems]
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [expandedIds, setExpandedIds] = useState(defaultExpandedIds);
  const filteredPrimaryItems = useMemo(
    () => filterNavItemsBySearch(primaryItems, searchQuery),
    [primaryItems, searchQuery]
  );
  const filteredDashboardItems = useMemo(
    () => filterNavItemsBySearch(dashboardItems, searchQuery),
    [dashboardItems, searchQuery]
  );
  const openIds = new Set(expandedIds);
  const hasSearchResults =
    filteredPrimaryItems.length > 0 || filteredDashboardItems.length > 0;

  function toggleExpanded(id: string) {
    setExpandedIds((currentIds) =>
      currentIds.includes(id)
        ? currentIds.filter((currentId) => currentId !== id)
        : [...currentIds, id]
    );
  }

  return (
    <aside
      className="admin-sidenav"
      aria-label="Admin navigation"
      data-collapsed={isCollapsed ? "true" : undefined}
    >
      <button
        className="admin-sidenav__mobile-toggle usa-button usa-button--outline"
        type="button"
        aria-expanded={isMenuOpen}
        aria-controls="admin-sidenav-menu"
        onClick={() => setIsMenuOpen((open) => !open)}
      >
        Menu
      </button>
      <nav
        className="admin-sidenav__nav"
        id="admin-sidenav-menu"
        data-open={isMenuOpen ? "true" : undefined}
      >
        <div className="admin-sidenav__search" role="search">
          <label className="usa-sr-only" htmlFor="admin-nav-search">
            Search navigation
          </label>
          <NavIcon name="search" />
          <input
            className="admin-sidenav__search-input"
            id="admin-nav-search"
            type="search"
            placeholder="Search"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
          />
        </div>

        <p className="admin-sidenav__title">
          <span className="admin-sidenav__label">{navigationTitle}</span>
        </p>

        <ul className="admin-sidenav__list">
          {filteredPrimaryItems.map((item) => (
            <li
              key={item.id}
              data-separator-before={item.separatorBefore || undefined}
            >
              {item.children?.length ? (
                <NavGroup
                  item={item}
                  currentPath={currentPath}
                  expanded={openIds.has(item.id)}
                  onToggle={() => toggleExpanded(item.id)}
                />
              ) : (
                <NavLink item={item} currentPath={currentPath} />
              )}
            </li>
          ))}
        </ul>

        {filteredDashboardItems.length > 0 ? (
          <div className="admin-sidenav__section admin-sidenav__section--dashboards">
            <p className="admin-sidenav__section-title">
              <span className="admin-sidenav__label">Dashboards</span>
            </p>
            <ul className="admin-sidenav__list">
              {filteredDashboardItems.map((item) => (
                <li key={item.id}>
                  <NavLink item={item} currentPath={currentPath} />
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {!hasSearchResults ? (
          <p className="admin-sidenav__empty" aria-live="polite">
            <span className="admin-sidenav__label">No menu items found.</span>
          </p>
        ) : null}

        <button
          className="admin-sidenav__collapse-button"
          type="button"
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          onClick={() => setIsCollapsed((collapsed) => !collapsed)}
        >
          <NavIcon name="collapse" />
          <span className="admin-sidenav__label">
            {isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          </span>
        </button>
      </nav>
    </aside>
  );
}
