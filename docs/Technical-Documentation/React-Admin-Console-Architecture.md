# React Admin Console: High-Level Architecture Document

**Issue:** #5746  
**Status:** Architecture Document (Technical Recommendation)  
**Date:** April 2026  
**Audience:** Development Team, Technical Leadership, DevOps

---

## Table of Contents

1. [Executive Summary](#executive-summary)
  - [8-Week Delivery Recommendation](#8-week-delivery-recommendation)
2. [Problem Statement](#problem-statement)
3. [Architecture Decision](#architecture-decision)
   - [Decision Matrix](#decision-matrix)
   - [Rationale](#rationale)
   - [Alternative: CRA-Integrated Admin Routes](#alternative-integrating-admin-routes-into-existing-cra-frontend)
4. [Detailed Architecture](#detailed-architecture)
  - [Architecture Principles](#architecture-principles)
  - [Boundary Recommendation](#boundary-recommendation)
5. [Technology Stack](#technology-stack)
  - [Form Strategy](#form-strategy)
6. [Data Access Patterns](#data-access-patterns)
  - [Workflow-to-Pattern Mapping](#workflow-to-pattern-mapping)
7. [Authentication & Authorization](#authentication--authorization)
  - [CSRF Strategy for Mutating Requests](#csrf-strategy-for-mutating-requests)
8. [API Integration Strategy](#api-integration-strategy)
  - [Recommended API Boundary](#recommended-api-boundary)
  - [How Next.js Accesses Data](#how-nextjs-accesses-data)
9. [Rendering Strategy](#rendering-strategy)
10. [Deployment Topology](#deployment-topology)
  - [Cloud.gov Considerations](#cloudgov-considerations)
11. [Code Sharing Strategy](#code-sharing-strategy)
12. [Large Dataset Handling](#large-dataset-handling)
13. [Migration Strategy](#migration-strategy)
14. [Risks & Mitigation](#risks--mitigation)
15. [Open Questions & Decisions](#open-questions--decisions)

---

## Executive Summary

**Recommendation: Build the React Admin Console as a standalone Next.js application** with server-side rendering (SSR) and React Server Components (RSC) capabilities for handling large tabular datasets and complex admin workflows.

**Alternative Considered:** Integrate admin routes into the existing Create React App (CRA) frontend. This approach trades ~2 weeks of initial development time for significant long-term performance and operational complexity. See [Alternative: Integrating Admin Routes into Existing CRA Frontend](#alternative-integrating-admin-routes-into-existing-cra-frontend) for detailed analysis.

**Delivery Constraint:** If implementation must ship within 2 months, the architecture should be pursued as an MVP-first rollout rather than a full parity replacement of every Django admin workflow.

### 8-Week Delivery Recommendation

If the delivery deadline is hard-capped at 8 weeks, the document recommends the following decision rule:

1. **If the team can narrow scope to an MVP:** build the admin console as a standalone Next.js app and ship only the highest-value workflows in the first release.
2. **If the team is expected to reach broad Django admin parity inside 8 weeks:** do not pretend the standalone plan is low-risk. In that case, integrating a limited admin surface into the existing CRA frontend is the safer schedule choice.

For this ticket, the recommended path remains **standalone Next.js**, but only with disciplined MVP scoping. The first release should focus on a narrow, production-usable slice such as:

- audit log viewing
- feature flag management
- user review and approval flows
- data file submission review and reparse initiation

The following should be treated as post-MVP work unless the team size is materially larger than assumed:

- full parsed-record browser parity
- deep error-report investigation views
- real-time updates
- advanced exports and reporting
- complete retirement of Django admin

### Why Next.js as a Standalone App?

- **Performance:** SSR + RSC move expensive data-fetching and initial rendering work off the browser, which is a better fit for large tabular datasets than a purely client-rendered route.
- **Separation of Concerns:** Decouples admin UI from user-facing frontend, reducing deployment coupling and enabling independent scaling
- **Preserves Backend Ownership:** Django remains the authoritative layer for authentication, authorization, business rules, workflow enforcement, and persistence.
- **Tech Stack Continuity:** Maintains React ecosystem while supporting modern server-side patterns unavailable in CRA
- **Flexibility:** Easier to customize admin workflows without affecting user-facing UX or bundle size
- **USWDS Integration:** Simpler to apply accessibility components consistently in an isolated context
- **Incremental Adoption:** Allows gradual migration from Django admin without full rewrite

**Key Characteristics:**
- Standalone Next.js 14+ application (independent from existing CRA frontend)
- Server-Side Rendering (SSR) for initial page loads
- React Server Components (RSC) for server-driven data workflows
- Optional thin BFF (Backend for Frontend) layer for admin-specific API shaping and aggregation
- Session-based authentication reusing existing Django auth infrastructure
- Django REST API remains the authoritative application API and policy boundary
- Cloud.gov deployment alongside existing frontend/backend

**Timeline Recommendation:** With an 8-week implementation ceiling, the recommended scope is a production-ready MVP focused on high-value admin workflows first, with advanced features such as live updates, column virtualization, and full parsed-record exploration deferred until after launch.

---

## Problem Statement

### Current State: Django Admin Limitations

The current Django admin serves as the primary administrative interface but has significant limitations:

1. **Tight Django ORM Coupling:** Django admin views are deeply coupled to ORM, making it difficult to implement custom business logic

2. **Poor Performance with Large Datasets:**
   - Parsed records table: Pagination breaks at scale
   - Error reports: N+1 query patterns cause latency
   - No native support for cursor-based streaming or RSC cache revalidation

3. **User Experience Gaps:**
   - Disjointed from React-based user frontend
   - Limited to Django admin's form system (incompatible with USWDS)
   - No support for modern interactive workflows (e.g., inline editing, real-time updates)

4. **Accessibility Compliance:**
   - Django admin has no built-in USWDS support
   - Section 508 compliance requires custom CSS overlays (high maintenance cost)
   - Inconsistent with user-facing interface accessibility standards

5. **Technology Debt:**
   - Tech stack divergence: Python backend + React frontend + Django admin HTML templates
   - Difficult for React-native developers to contribute to admin workflows
   - Conflicts with longer-term goal of decoupling presentation from Django

### Admin Workflows Requiring Support

The following workflows are currently managed through Django admin and must be replicated:

1. **User Management**
   - Approve/reject user account requests
   - Manage user roles and STT assignments
   - Handle soft delete operations
   - View change request audit logs

2. **Data File Submission Review**
   - View submitted data files by STT/quarter/year
   - Inspect parsing status and outcomes
   - Trigger reparse on failed submissions
   - Download submission logs

3. **Parsed Record Inspection**
   - Browse parsed records from large datasets (thousands of rows)
   - Filter by error status, record type, program
   - Export subset of records for analysis
   - Drill-down into error details

4. **Error Report Viewing**
   - View error reports grouped by file/section
   - Search/filter errors by code and message
   - Track error resolution across reparse cycles

5. **Feature Flag Management**
   - Enable/disable features per environment
   - Edit feature configuration (JSON payloads)
   - Version control via audit trail

6. **Audit Logging**
   - View all administrative changes (LogEntry)
   - Filter by user/resource/timestamp
   - Export audit trail for compliance

---

## Architecture Decision

### Decision: Standalone Next.js Application

**Choice:** Build the React Admin Console as a **standalone Next.js 14+ application** rather than integrating admin routes into the existing Create React App (CRA) frontend.

### Decision Matrix

| Criterion | Standalone Next.js | Integrated CRA Routes | Notes |
|-----------|-------------------|-----------------------|-------|
| **Performance with Large Datasets** | 5 | 3 | Next.js RSC/SSR is superior for server-driven workflows |
| **Deployment Independence** | 5 | 2 | Standalone allows independent scaling and deployment |
| **Development Velocity** | 4 | 3 | Fewer interdependencies, faster iteration in isolation |
| **Shared Component Reuse** | 3 | 5 | Monorepo patterns can still share components |
| **USWDS Integration** | 5 | 4 | Cleaner CSS scoping and component isolation |
| **Tech Stack Clarity** | 4 | 3 | Reduces confusion (Next.js vs. CRA patterns) |
| **Learning Curve** | 4 | 4 | Both require Next.js knowledge; standalone is clearer |
| **Incremental Migration** | 5 | 3 | Can migrate views one at a time without deployment coupling |

Note: 1 Lowest rating and 5 highest rate

### Rationale

1. **Deployment Flexibility:** Standalone deployment allows scaling admin and user-facing apps independently based on demand patterns (admin traffic is typically lower and asynchronous)

2. **Rendering Strategy Optimization:** Next.js RSC shines in admin contexts where server-driven workflows dominate. CRA's client-side rendering adds unnecessary latency for initial table loads.

3. **Incremental Migration:** Each Django admin page can be migrated independently to the React admin console without requiring a monolithic update of both apps

4. **Team Structure:** Common pattern in orgs where admin engineering is separate from user-facing product teams; separate repos can support this organizational structure

5. **USWDS Consistency:** Easier to maintain USWDS compliance across a focused admin UI without interaction effects from user-facing pages

---

## Alternative: Integrating Admin Routes into Existing CRA Frontend

This section evaluates the alternative approach of adding admin routes directly into the existing Create React App (CRA) frontend, rather than building a separate Next.js application.

Unless otherwise stated, the comparisons in this section are qualitative architecture trade-offs rather than benchmarked TDP measurements.

### Architecture Overview: CRA-Integrated Edition

```
┌─────────────────────────────────────┐
│   Admin User Browser                │
└─────────────────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────┐
    │  tdrs-frontend (CRA)        │
    ├─────────────────────────────┤
    │  User Routes:               │
    │  • /dashboard               │
    │  • /profile                 │
    │  • /submissions             │
    │                             │
    │  Admin Routes (NEW):        │
    │  • /admin/users             │
    │  • /admin/submissions       │
    │  • /admin/records           │
    │  • /admin/errors            │
    │  • /admin/features          │
    │  • /admin/audit-logs        │
    │                             │
    │  Shared Components/State:   │
    │  • Redux store              │
    │  • API client               │
    │  • Auth context             │
    └─────────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────┐
    │  Django REST API            │
    │  (existing)                 │
    └─────────────────────────────┘
```

### Comparison: Standalone Next.js vs. CRA-Integrated

| Criterion | Standalone Next.js | CRA-Integrated Admin | Winner |
|-----------|-------------------|-----------------------|--------|
| **Initial Build Effort** | 2-3 weeks scaffold + architecture | 1-2 weeks (add routes to existing app) | CRA has the advantage |
| **Performance (Large Datasets)** | Better first content and lower browser work | Higher browser work and slower perceived load on data-heavy screens | Next.js has the advantage |
| **Client-Side Bundle Size** | Admin code isolated from main user bundle | Higher risk of main frontend bundle growth | Next.js has the advantage |
| **Time-to-Interactive (TTI)** | Typically better for data-heavy initial views | Typically worse for data-heavy initial views | Next.js has the advantage |
| **Mobile Experience** | Mobile-optimized SSR | CSR bottleneck on low-end devices | Next.js has the advantage |
| **Deployment Complexity** | Separate CI/CD pipeline | Single deploy (coupled) | CRA has the advantage if minimizing app count is the priority |
| **Scaling Independently** | Supported | Not supported | Next.js has the advantage |
| **Shared Component Reuse** | Requires monorepo setup | In same repo | CRA has the advantage |
| **USWDS Component Integration** | Clean (isolated app) | Potential CSS conflicts | Next.js has the advantage |
| **Development Velocity (Phases 2+)** | Fast (independent team) | Medium (shared codebase) | Next.js has the advantage |
| **Learning Curve** | Developers learn Next.js App Router | Stick with familiar CRA + React Router | CRA has the advantage |
| **Testing Infrastructure** | New test setup required | Reuse existing setup | CRA has the advantage |
| **Complexity for Ops/DevOps** | Two containers to manage | Single container | CRA has the advantage if operational simplicity is the priority |
| **State Management Complexity** | Simpler (server-driven via RSC) | Requires Redux enhancements | Next.js has the advantage |

---

### CRA-Integrated Approach: Detailed Analysis

#### Advantages

1. **Reuse Existing Infrastructure**
   - No separate CI/CD pipeline; use existing GitHub Actions
   - Same deployment process (single `npm run build` → single Cloud.gov push)
   - Share test infrastructure and linting setup
   - Existing Dockerfile can build both user and admin routes

2. **Shared Components & Utilities**
   - All USWDS components, hooks, utilities in one codebase
   - Redux store for both user and admin state
   - API client shared directly (no BFF layer to maintain)
   - Types and constants in single location

3. **Lower Initial Effort**
   - No new project scaffolding or tooling setup
   - Developers already know CRA patterns
   - React Router 6 supports nested routes/layouts naturally
  - Faster time-to-first-admin-page (1-2 weeks vs. 2-3 weeks)

4. **Simpler Operations**
   - Single deployment per release cycle
   - Single monitoring/alerting setup
   - Operations team manages one application
   - Logs in same container; easier debugging

5. **Consistency**
   - All routes use same HTTP security headers
   - Session management identical for user and admin flows
   - Styling via same SCSS setup
   - Font Awesome icons, USWDS versions matched automatically

#### Disadvantages

1. **Performance: Large Datasets Suffer** ⚠️
   - **Bundle Size:** Admin routes add 50-100KB to JS bundle (pagination, data grid, filters)
   - **First Paint:** CRA requires full JS download → parse → execute → render
  - **Comparison:** SSR typically improves first content and reduces browser-side work compared with client-side rendering of data-heavy screens
   - **Large Tables:** Renderingparsed records table with 10k rows in browser = jank
   - **Pagination Workaround:** Must paginate on frontend; increases API calls

   ```javascript
   // CSR approach (inefficient for large result sets)
   const [records, setRecords] = useState([])
   
   useEffect(() => {
     // Fetch ALL matching records (terrible at scale)
     API.get('/parsed_records?file_id=123')
       .then(data => setRecords(data))
   }, [])
   
   // Render 100 per page client-side (after 1s+ fetch latency)
   const paginated = records.slice((page-1)*100, page*100)
   ```

   versus SSR:
   ```typescript
   // Server Component (efficient at scale)
   async function RecordsPage({ searchParams }) {
     const page = parseInt(searchParams.page || '1')
     const records = await fetch(`/api/records?page=${page}`)
     return <RecordsTable records={records} />
   }
   // Returns pre-rendered HTML from the server before the client finishes hydrating
   ```

2. **Deployment Coupling**
   - Admin and user features share single deployment
   - Admin bug crashes entire frontend (and vice versa)
   - Must coordinate release cycles (slower if admin work is on separate cadence)
   - Rollback of one feature affects both

3. **Bundle Bloat**
   - Every user downloads admin code (even though they can't access it)
   - Data grid libraries (TanStack Table, ag-Grid) add 30-50KB
   - Form builders, export utilities, etc. increase payload
   - Workaround: Dynamic imports reduce impact slightly, but still added complexity

4. **State Management Complexity**
   - Redux store grows with admin slices (users, submissions, approvals, etc.)
   - Potential naming conflicts (e.g., `admin/users` vs. `data/users`)
   - Admin state mutations could accidentally affect user state
   - Requires disciplined architecture to avoid spaghetti coupling

5. **Dependency Version Conflicts**
   - Admin might need newer React Router patches (breaking for user routes)
   - UI library updates could conflict (USWDS version bump affects both)
   - Testing library upgrades must be coordinated
   - Harder to use experimental features without risk to user experience

6. **Scaling/Performance Tuning**
   - Can't scale admin independently if traffic pattern differs
   - Resource-intensive admin queries (error reports, large exports) compete with user traffic
   - Harder to profile admin performance separately
   - CDN caching strategy must account for both app types

7. **USWDS CSS Management**
   - Admin needs strict USWDS compliance; user frontend may relax some rules
   - CSS scope conflicts (admin might need different color scheme for form fields)
   - Utility class naming could collide
   - Harder to maintain separate visual languages if needed

---

### Code Structure: CRA-Integrated Option

```
tdrs-frontend/
├── src/
│   ├── components/
│   │   ├── admin/                          # NEW: Admin-only components
│   │   │   ├── users/
│   │   │   │   ├── UserList.tsx
│   │   │   │   ├── UserDetail.tsx
│   │   │   │   └── UserFilters.tsx
│   │   │   ├── submissions/
│   │   │   │   ├── SubmissionList.tsx
│   │   │   │   └── SubmissionDetail.tsx
│   │   │   ├── records/
│   │   │   │   ├── RecordsDataGrid.tsx
│   │   │   │   └── RecordsFilters.tsx
│   │   │   ├── errors/
│   │   │   │   └── ErrorReportViewer.tsx
│   │   │   ├── audit-logs/
│   │   │   │   └── AuditLogTable.tsx
│   │   │   ├── features/
│   │   │   │   ├── FeatureFlagList.tsx
│   │   │   │   └── FeatureFlagEditor.tsx
│   │   │   └── _common/
│   │   │       ├── AdminNav.tsx
│   │   │       ├── AdminHeader.tsx
│   │   │       ├── AdminLayout.tsx
│   │   │       ├── DataGrid.tsx             # Shared complex table
│   │   │       └── AdminGuard.tsx           # Authorization wrapper
│   │   ├── user/                           # Existing user routes
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Profile.tsx
│   │   │   └── ...
│   │   └── common/                         # Shared across both
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── ...
│   ├── actions/
│   │   ├── admin/                          # NEW
│   │   │   ├── users.js
│   │   │   ├── submissions.js
│   │   │   └── ...
│   │   ├── data/                           # Existing
│   │   │   └── ...
│   ├── reducers/
│   │   ├── admin/                          # NEW
│   │   │   ├── users.js
│   │   │   ├── submissions.js
│   │   │   └── ...
│   │   ├── data/                           # Existing
│   │   │   └── ...
│   ├── selectors/
│   │   ├── admin/                          # NEW
│   │   │   └── ...
│   ├── pages/
│   │   ├── admin/                          # NEW
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Users.tsx
│   │   │   ├── Submissions.tsx
│   │   │   ├── Records.tsx
│   │   │   ├── Errors.tsx
│   │   │   ├── Features.tsx
│   │   │   └── AuditLogs.tsx
│   │   └── user/                           # Existing
│   │       ├── Home.tsx
│   │       └── ...
│   ├── App.tsx                             # Route configuration
│   └── index.tsx
└── package.json
```

#### Updated Routes in App.tsx

```typescript
// src/App.tsx
import AdminLayout from './components/admin/_common/AdminLayout'
import PrivateRoute from './components/PrivateRoute'
import AdminGuard from './components/admin/_common/AdminGuard'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* User routes (existing) */}
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/submissions" element={<PrivateRoute><Submissions /></PrivateRoute>} />
        
        {/* Admin routes (NEW) - protected by AdminGuard */}
        <Route
          path="/admin/*"
          element={
            <PrivateRoute>
              <AdminGuard>
                <AdminLayout />
              </AdminGuard>
            </PrivateRoute>
          }
        >
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="users" element={<UserList />} />
          <Route path="users/:id" element={<UserDetail />} />
          <Route path="submissions" element={<SubmissionList />} />
          <Route path="submissions/:id" element={<SubmissionDetail />} />
          <Route path="records" element={<RecordsDataGrid />} />
          <Route path="records/:id" element={<RecordDetail />} />
          <Route path="errors" element={<ErrorReportViewer />} />
          <Route path="features" element={<FeatureFlagList />} />
          <Route path="features/:id" element={<FeatureFlagEditor />} />
          <Route path="audit-logs" element={<AuditLogTable />} />
        </Route>

        {/* Default route */}
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  )
}
```

---

### Performance Impact Analysis: CRA vs. Next.js for Large Tables

The sequences below are illustrative examples to show where work happens in each architecture. They are not measured timings from a TDP prototype.

#### Scenario: Browsing 5,000 parsed records

**CRA Approach:**
```
Time     Activity
────────────────────────────────────────
0ms      User clicks "View Records"
~        React Router navigates
~        Component mounts and kicks off client-side fetch
~        Large JSON payload is downloaded and parsed in the browser
~        Table render work happens on the client
~        Page becomes interactive after client processing completes
```

**Next.js + SSR Approach:**
```
Time     Activity
────────────────────────────────────────
0ms      User clicks "View Records"
~        Server fetches a page of results
~        Server renders HTML
~        Browser receives already-rendered content
~        Hydration completes for interactive controls
~        User can interact sooner because less data processing happens in the browser
```

**Result:** Next.js is a better fit for data-heavy admin surfaces because it reduces client-side work and makes server-side pagination, streaming, and response shaping first-class concerns.

---

### Redux State Management: Complexity in CRA Approach

Adding admin functionality to Redux requires careful namespace isolation:

```javascript
// store/index.js - GROWING COMPLEXITY
const store = {
  // User scope
  auth: authReducer,
  user: userReducer,
  submissions: submissionsReducer,
  
  // Admin scope (NEW) - potential naming conflicts
  admin: combineReducers({
    users: adminUsersReducer,          // Different from user.users!
    submissions: adminSubmissionsReducer, // Overlaps with user submissions
    approvals: adminApprovalsReducer,
    changes: changeRequestsReducer,
    records: recordsReducer,
    errors: errorsReducer,
    features: featureFlagsReducer,
    auditLogs: auditLogsReducer,
    paging: adminPagingReducer,
    filters: adminFiltersReducer,
  })
}

// Real example of potential conflict:
// action: user/submissions/FETCH_START
// action: admin/submissions/FETCH_START
// Both trigger loading states, but in different parts of store
```

**CRA Workaround:** Use Redux namespacing + selector factories (more boilerplate).

**Next.js Approach:** Server state (via RSC) + minimal client state (URL + local component state) = simpler mental model.

---

### Bundle Size Comparison

The table below is illustrative only. Use bundle analysis during implementation planning to establish a real baseline and regression budget.

```
Metric                        | CRA (User Only) | CRA (User+Admin) | Next.js Admin-Only | Savings
──────────────────────────────|─────────────────|──────────────────|────────────────────|────────
React + React DOM             | 40KB            | 40KB             | 0KB (server-side)  | -
React Router v6               | 12KB            | 12KB             | 0KB (file-based)   | -
Redux + Redux Thunk           | 18KB            | 18KB             | 0KB (no client state) | -
USWDS Components              | 25KB            | 25KB             | 25KB               | -
TanStack Table (data grid)    | -               | 35KB             | 35KB               | -
Admin Feature Code            | -               | 60KB             | 60KB (server only) | 60KB
Form Builders / Validators    | -               | 20KB             | 5KB (onload)       | 15KB
Charts / Analytics            | -               | 15KB             | 15KB               | -
──────────────────────────────|─────────────────|──────────────────|────────────────────|────────
**Total JavaScript**          | **130KB**       | **240KB**        | **140KB**          | **User saves 100KB!**
```

**Note:** This assumes Next.js serves admin to admins only (no user exposure). CRA bundles admin code for all users.

---

### When CRA-Integration Makes Sense

CRA-integrated admin could be viable if:

1. **Admin workflows are simple** (CRUD only, no large tables)
  - Good candidate: feature flags
  - Good candidate: audit logs
  - Good candidate: user approvals
   
  In contrast, parsed records and error reports are weak candidates for a CRA-integrated approach because they are more data-heavy and filter-heavy.

2. **Limited async/real-time requirements**
   - No Server Sent Events for live job progress
   - No streaming updates to dashboards
   - No cursor-based pagination

3. **Performance Requirements are Relaxed**
   - Admin users accept 2-3s page loads
   - Large table pagination is acceptable
   - Mobile admin access is not priority

4. **Team Prefers Monolithic Deployment**
   - Single deploy cycle acceptable
   - Shared testing/CI pipeline desired
   - Operations team prefers single container

---

### Hybrid Recommendation: Phase the Decision

If the delivery deadline is truly capped at 8 weeks, there are two viable execution patterns:

**Option A: Fastest path to first release**
- Add a narrow set of admin routes to the existing CRA frontend
- Limit scope to simpler workflows such as feature flags, audit logs, and selected approval flows
- Accept that this is a tactical delivery choice, not the best long-term architecture

**Option B: Recommended architecture with MVP scoping**
- Build a standalone Next.js admin app immediately
- Limit the first release to workflows that can fit inside the 8-week window
- Defer full parsed-record browsing, advanced exports, live updates, and deep reporting features until a later increment

For TDP, Option B remains the better architectural choice if the team can keep the first release intentionally narrow. If leadership expects full Django admin replacement within 2 months, Option B is not realistic without significant staffing or reduced parity expectations.

---

## Final Recommendation Rationale

**Choose: Standalone Next.js** for the following reasons:

| Factor | Impact |
|--------|--------|
| **Performance** | Next.js better supports server-rendered, paginated, and streamed admin views without pushing heavy data processing into the browser |
| **Operational Scaling** | Admin and user traffic patterns differ; independent scaling is valuable |
| **Future-Proofing** | Real-time updates, exports, streaming = all easier in Next.js |
| **USWDS Compliance** | Isolated app = cleaner CSS scoping; less risk of conflicts |
| **Code Maintainability** | Separate codebase reduces coupling; admin changes don't affect user experience |
| **Tech Diversity** | Next.js is increasingly standard for admin dashboards in React orgs |
| **Budget/Timeline Trade-off** | Slightly higher upfront setup cost than CRA integration, but a better long-term fit if the first release is constrained to an MVP |

**However:** If the team must deliver visible admin functionality inside 8 weeks and cannot narrow scope, CRA integration is the lower-risk schedule choice. If the team can narrow scope to an MVP, standalone Next.js remains the recommended target architecture.

---

## Detailed Architecture

### Architecture Principles

1. **Django remains authoritative.** Authentication, authorization, business rules, audit logging, and persistence remain in Django.
2. **Next.js is an application shell, not a replacement backend.** Its responsibilities are rendering, route protection, response shaping, and orchestration.
3. **Prefer API reuse over policy duplication.** The admin console should call Django APIs or narrowly scoped admin-specific endpoints rather than reimplementing business logic in Node.js.
4. **Use a BFF only where it adds value.** The BFF is appropriate for response shaping, aggregation, pagination adaptation, and admin-specific UX concerns. It should not become a second domain backend.
5. **Keep reads and writes honest.** All writes and permission-sensitive reads should flow through Django-controlled endpoints.

### High-Level Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Admin User Browser                      │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────┐
        │   React Admin Console (Next.js 14+)      │
        ├──────────────────────────────────────────┤
        │  • Server Components (RSC)               │
        │  • Server-Side Rendering (SSR)           │
        │  • Data layer (BFF integration)          │
        │  • USWDS Component Library                │
        │  • Session/Auth Middleware               │
        └──────────────────────────────────────────┘
                        │              │
         ┌──────────────┘              └──────────────┐
         │                                            │
         ▼                                            ▼
   ┌──────────────┐                            ┌──────────────┐
  │  Django Auth │                            │ Django REST  │
  │  Sessions    │                            │ API          │
   │  (Cookies)   │                            │              │
   └──────────────┘                            └──────────────┘
         │                                            │
         └──────────────────────┬─────────────────────┘
                                ▼
                    ┌──────────────────────┐
                    │   tdrs-backend       │
                    │   (Django REST)      │
                    │                      │
                    │  • Authentication    │
                    │  • Authorization     │
                    │  • Business Logic    │
                    │  • Audit / Workflow  │
                    │  • Database (PostgreSQL) │
                    └──────────────────────┘
```

### Boundary Recommendation

The recommended request path is:

`Browser -> Next.js admin app -> Django API -> PostgreSQL`

The Next.js layer may expose internal route handlers as a thin BFF for admin-specific shaping, but it should not connect directly to PostgreSQL for the MVP and should not bypass Django permission checks, audit hooks, or workflow rules. If direct database access is ever considered for a narrow read-only reporting case, it should require a separate ADR, explicit read-only credentials, and a documented justification.

### Application Structure

```
tdrs-admin/
├── app/
│   ├── (auth)/                        # Auth pages (login callback, logout)
│   │   ├── login/
│   │   └── logout/
│   ├── admin/                         # Protected admin routes
│   │   ├── layout.tsx                 # Admin shell (nav, sidebar)
│   │   ├── users/
│   │   │   ├── page.tsx               # User list (Server Component + RSC)
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx           # User detail/edit
│   │   │   ├── _components/
│   │   │   │   ├── UserTable.tsx      # Shared table component
│   │   │   │   └── UserFilters.tsx    # Filter controls
│   │   ├── submissions/
│   │   │   ├── page.tsx               # Data files list
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx           # Submission detail
│   │   │   └── _components/
│   │   │       ├── SubmissionTable.tsx
│   │   │       └── ParseStatusBadge.tsx
│   │   ├── records/
│   │   │   ├── page.tsx               # Parsed records browser
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx           # Record detail
│   │   │   └── _components/
│   │   │       └── RecordsDataGrid.tsx
│   │   ├── errors/
│   │   │   ├── page.tsx               # Error report viewer
│   │   │   └── _components/
│   │   │       └── ErrorReportTable.tsx
│   │   ├── features/
│   │   │   ├── page.tsx               # Feature flags list
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx           # Feature flag edit
│   │   │   └── _components/
│   │   │       └── FeatureFlagEditor.tsx
│   │   ├── audit-logs/
│   │   │   ├── page.tsx               # Audit log viewer
│   │   │   └── _components/
│   │   │       └── LogEntryTable.tsx
│   │   └── _components/
│   │       ├── AdminNav.tsx           # Sidebar navigation
│   │       ├── AdminHeader.tsx        # Top header bar
│   │       └── ProtectedLayout.tsx    # Auth guard wrapper
│   ├── api/                           # BFF Backend for Frontend
│   │   ├── users/
│   │   │   ├── route.ts               # Proxy: GET /v1/users
│   │   │   ├── [id]/route.ts          # Proxy: GET/PATCH /v1/users/{id}
│   │   │   └── change-requests/route.ts # Proxy: GET /v1/users/change-requests
│   │   ├── submissions/
│   │   │   ├── route.ts               # Proxy: GET /v1/data_files
│   │   │   ├── [id]/route.ts          # Proxy: GET /v1/data_files/{id}
│   │   │   └── [id]/reparse/route.ts  # Custom: POST reparse trigger
│   │   ├── records/
│   │   │   ├── route.ts               # Custom: GET parsed records (requires join)
│   │   │   └── [id]/route.ts          # Custom: GET record detail
│   │   ├── audit-logs/route.ts        # Proxy: GET /v1/logs
│   │   └── features/
│   │       ├── route.ts               # Proxy: GET/POST /v1/feature-flags
│   │       └── [id]/route.ts          # Proxy: GET/PATCH /v1/feature-flags/{id}
│   └── page.tsx                       # Index redirect
├── lib/
│   ├── api-client.ts                  # Fetch wrapper (BFF calls)
│   ├── auth.ts                        # Django session validation and admin identity helpers
│   ├── permissions.ts                 # Admin role/permission checks
│   ├── validators.ts                  # Form/data validators
│   ├── types.ts                       # Shared TypeScript types
│   └── hooks/
│       ├── useAuth.ts                 # Auth context hook
│       ├── useTableState.ts           # Table pagination/sorting state
│       └── useFetch.ts                # SWR wrapper for client components
├── components/
│   ├── ui/                            # USWDS wrapped components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   ├── Table.tsx                  # Custom table for pagination
│   │   └── Alert.tsx
│   ├── tables/                        # Complex data grid components
│   │   ├── PaginatedTable.tsx         # Page-based pagination
│   │   ├── CursorTable.tsx            # Cursor-based pagination (for very large sets)
│   │   └── ColumnToggler.tsx          # Allow hiding/showing columns
│   └── forms/
│       ├── FormField.tsx
│       └── FormBuilder.tsx            # Dynamic form renderer
├── middleware.ts                      # Authentication middleware
├── next.config.js                     # Next.js configuration
└── package.json
```

---

## Technology Stack

### Core Framework & Rendering

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Framework** | Next.js | 14+ | Modern RSC support, file-based routing, built-in optimization |
| **React** | React | 18.2+ | Server Components, concurrent features |
| **Rendering** | SSR + RSC | Default | Server-driven workflows, streaming support |
| **Data Fetching** | Server Components + fetch() | Built-in | Server-side calls to Django API or thin BFF endpoints, avoiding client-side waterfalls |

### UI & Styling

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **UI Library** | USWDS React | 6.0+ | Section 508 compliance built-in, accessibility components |
| **CSS-in-JS** | Tailwind CSS | 3.3+ | Utility-first for rapid iteration; USWDS components pre-configured |
| **Icons** | Font Awesome / USWDS Icons | Latest | Consistent with user-facing frontend |

### Authentication & Security

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Session Management** | Next.js cookies | Reuse existing Django session cookies; stateless validation |
| **CSRF Protection** | Next.js built-in | Automatic CSRF token generation |
| **Role-Based Access Control (RBAC)** | Custom middleware | Parse user permissions from Django auth system |

### State Management

| Component | Technology | Context |
|-----------|-----------|---------|
| **Server State** | React Server Components | Default for data fetching and display |
| **Client State** | React Context + useState | Minimal client-side state (filters, modal open/close) |
| **Client-Side Caching** | SWR or TanStack Query | For interactive client components only |

### Forms & Validation

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Form Framework** | React Hook Form | Lightweight, compatible with RSC integration patterns |
| **Validation** | Zod or Yup | Type-safe schema validation |
| **File Upload** | React Drop Zone + AWS S3 | Consistent with user-facing frontend pattern |

### Form Strategy

The admin console should use a hybrid form strategy:

1. **Server-rendered read views, client-rendered edit surfaces.** Detail pages and review screens can be server-rendered, while forms that require client validation or conditional interaction should use client components.
2. **React Hook Form plus schema validation.** Use React Hook Form with Zod for client-side ergonomics, but treat Django validation and permission checks as authoritative.
3. **Do not duplicate domain rules in the browser.** The browser may validate field shape and required values, but workflow rules, permission checks, and final validation outcomes belong in Django.
4. **Use explicit mutation endpoints for workflows.** Reparsing, approvals, feature-flag updates, and other workflow-heavy actions should go through dedicated endpoints rather than generic CRUD where that improves auditability and safety.
5. **Prefer pessimistic updates for admin workflows.** Most admin operations should show confirmed backend state after mutation rather than optimistic local state, because auditability and correctness matter more than UI speed.
6. **Preserve drafts only where needed.** For longer forms, store unsaved client drafts locally and warn before navigation, but avoid creating a second source of truth for persisted data.

### Data Grid & Tables

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Table Rendering** | Custom + TanStack Table (React Table) | Headless for control; USWDS styling wrapper |
| **Large Dataset Handling** | Server-side pagination + RSC | Cursor-based pagination for >10k rows |
| **Column Configuration** | Custom column builder | Save/restore preferences (localStorage or DB) |

### API Client

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **HTTP Client** | Native fetch() | Built into Node.js/Next.js; no external dep |
| **Request Signing** | Django session cookies | Inherit session auth from browser |
| **Error Handling** | Custom error boundary + alerts | Consistent UX for API failures |

### Testing & Quality

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Component Testing** | Vitest + React Testing Library | Same stack as existing frontend |
| **E2E Testing** | Cypress or Playwright | Test complete user journeys |
| **Linting** | ESLint + Prettier | Consistent code style |
| **Type Checking** | TypeScript | Full static typing |

### Development Tools

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Package Manager** | Yarn 4.6+ | Match existing frontend setup |
| **Build Tool** | Next.js built-in | Zero-config optimization |
| **Dev Server** | Next.js dev mode | HMR + RSC debugging |

---

## Data Access Patterns

### Pattern 1: Server-Side API Access for Read-Heavy Screens

**Use Case:** User list page, submitted files list, audit logs

```typescript
// app/admin/users/page.tsx
import { fetchUsers, fetchUserCount } from '@/lib/server/users'

interface UserListPageProps {
  searchParams: { page?: string; sort?: string }
}

export default async function UserListPage({ searchParams }: UserListPageProps) {
  const page = parseInt(searchParams.page || '1', 10)
  const sort = searchParams.sort || '-created_at'
  
  // Server-side: Fetch data through Django-owned APIs, optionally shaped by a BFF
  // Returns paginated results + total count
  const [users, totalCount] = await Promise.all([
    fetchUsers({ page, sort, limit: 25 }),  // Calls BFF: /api/users?page=1&sort=-created_at
    fetchUserCount(), // Calls BFF: /api/users/count
  ])

  return (
    <div>
      <UserTable users={users} />
      <Paginator 
        current={page} 
        total={totalCount}
        limit={25}
      />
    </div>
  )
}
```

**Data Flow:**
1. Server Component renders (server-side rendering)
2. `fetchUsers()` calls BFF endpoint (Next.js `/api/users`)
3. BFF endpoint authenticates request using Django session cookie
4. BFF proxies to Django REST API (`GET /v1/users?page=1`)
5. Django backend queries database, returns paginated JSON
6. BFF passes response to Server Component
7. HTML streamed to browser

**Advantages:**
- No client-side JS execution needed for data fetching
- Session cookie automatically included (no JWT token management)
- Database queries optimized (N+1 patterns solvable at BFF layer)
- Large datasets streamed efficiently

---

### Pattern 2: RSC with Progressive Enhancement (Interactive Filters)

**Use Case:** User list with real-time filtering/sorting

```typescript
// app/admin/users/page.tsx
'use client' // Interactive layer only

import { Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import UserTable from './_components/UserTable'
import UserTableSkeleton from './_components/UserTableSkeleton'

export default function UserListPage() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const handleFilterChange = (filters: { searchTerm?: string; status?: string }) => {
    // Update URL params → triggers Server Component re-render
    const params = new URLSearchParams(searchParams)
    if (filters.searchTerm) params.set('search', filters.searchTerm)
    if (filters.status) params.set('status', filters.status)
    router.push(`?${params.toString()}`)
  }

  return (
    <div>
      <UserFilters onChange={handleFilterChange} />
      
      {/* Suspense boundary for streaming */}
      <Suspense fallback={<UserTableSkeleton />}>
        <UserTableAsync searchParams={searchParams} />
      </Suspense>
    </div>
  )
}

// Server Component (child of above Client Component)
async function UserTableAsync({ searchParams }: { searchParams: URLSearchParams }) {
  const users = await fetchUsers({
    search: searchParams.get('search'),
    status: searchParams.get('status'),
  })
  return <UserTable users={users} />
}
```

**Data Flow:**
1. User changes filter (Client Component event)
2. URL updates (`?status=approved`)
3. Server Component re-renders with new params
4. Suspense boundary shows skeleton while loading
5. BFF queries updated results
6. HTML streamed to replace table

**Advantages:**
- URL is source of truth for filters
- Browser back/forward buttons work naturally
- Server-side filtering reduces data transfer
- Skeleton UI provides perceived performance

---

### Pattern 3: Search Results with Streaming

**Use Case:** Parsed records search (especially >10k results)

```typescript
// app/admin/records/page.tsx
import { ReactNode } from 'react'
import { Suspense } from 'react'
import RecordStreamTable from './_components/RecordStreamTable'
import RecordTableSkeleton from './_components/RecordTableSkeleton'

interface RecordsPageProps {
  searchParams: { q?: string; file_id?: string; cursor?: string }
}

export default async function RecordsPage({ searchParams }: RecordsPageProps) {
  return (
    <div>
      <RecordSearchForm />
      
      <Suspense fallback={<RecordTableSkeleton />}>
        <RecordStream searchParams={searchParams} />
      </Suspense>
    </div>
  )
}

// Server Component: Renders streaming results
async function RecordStream({ searchParams }: RecordsPageProps) {
  const pageSize = 100
  const cursor = searchParams.cursor
  
  // Fetch current page + "hasNext" indicator for cursor
  const response = await fetchRecords({
    query: searchParams.q,
    fileId: searchParams.file_id,
    cursor,
    limit: pageSize + 1, // Fetch extra to detect "more"
  })

  const hasMore = response.records.length > pageSize
  const records = response.records.slice(0, pageSize)
  const nextCursor = hasMore ? records[records.length - 1].id : null

  return (
    <>
      <RecordTable records={records} />
      
      {hasMore && (
        <LoadMoreButton 
          nextCursor={nextCursor}
          searchParams={searchParams}
        />
      )}
    </>
  )
}
```

**Data Flow:**
1. Server Component fetches page of results (limit + 1 to detect "more")
2. Renders first page to browser
3. Client can click "Load More" → URL update with cursor
4. Next page streams in without page reload

**Advantages:**
- Handles large result sets efficiently
- Cursor-based pagination (no offset problems at scale)
- Progressive loading improves time-to-first-content

---

### Pattern 4: Complex Workflows via BFF mutations

**Use Case:** Bulk reparse trigger, user approval workflow

```typescript
// app/api/submissions/[id]/reparse/route.ts (BFF Layer)
import { NextRequest, NextResponse } from 'next/server'

async function getAuthenticatedAdminContext(request: NextRequest) {
  const response = await fetch(`${process.env.DJANGO_API_URL}/v1/auth_check`, {
    headers: {
      Cookie: request.headers.get('cookie') || '',
    },
    cache: 'no-store',
  })

  if (!response.ok) return null
  return response.json()
}

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const actor = await getAuthenticatedAdminContext(request)
  if (!actor) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const payload = await request.json()

  // Load current submission state
  const fileResponse = await fetch(
    `${process.env.DJANGO_API_URL}/v1/data_files/${params.id}`,
    { headers: { Cookie: request.headers.get('cookie') || '' } }
  )
  const currentFile = await fileResponse.json()

  // Check authorization
  if (!actor.is_admin && actor.stt_id !== currentFile.stt_id) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
  }

  // Trigger reparse through Django so that workflow rules and audit hooks stay centralized
  const reparseResponse = await fetch(
    `${process.env.DJANGO_API_URL}/v1/data_files/${params.id}/actions/reparse`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || '',
        'X-CSRFToken': request.headers.get('x-csrftoken') || '',
      },
      body: JSON.stringify({
        reason: payload.reason,
        triggered_by: actor.id,
      }),
    }
  )

  if (!reparseResponse.ok) {
    return NextResponse.json(
      { error: 'Failed to trigger reparse' },
      { status: reparseResponse.status }
    )
  }

  return NextResponse.json({ success: true })
}
```

**Client-side invocation:**

```typescript
// Client Component or Server Action
export async function triggerReparse(fileId: string, reason: string) {
  const response = await fetch(`/api/submissions/${fileId}/reparse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason }),
  })

  if (!response.ok) throw new Error('Reparse failed')
  return response.json()
}
```

**Advantages:**
- BFF layer centralizes authorization logic
- Can implement complex workflows (multi-step state transitions)
- Sensitive operations kept server-side
- Django session cookies automatically included
- Django remains the only place where workflow authorization and audit behavior are enforced

---

### Pattern 5: Real-Time Updates via Server Sent Events (optional, post-MVP)

**Use Case:** Admin watches parsing progress live

```typescript
// app/api/submissions/[id]/events/route.ts
import { NextRequest } from 'next/server'

async function getAuthenticatedAdminContext(request: NextRequest) {
  const response = await fetch(`${process.env.DJANGO_API_URL}/v1/auth_check`, {
    headers: {
      Cookie: request.headers.get('cookie') || '',
    },
    cache: 'no-store',
  })

  if (!response.ok) return null
  return response.json()
}

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const actor = await getAuthenticatedAdminContext(request)

  // Check auth
  if (!actor?.is_admin) {
    return new Response('Forbidden', { status: 403 })
  }

  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      while (true) {
        // Poll Django for status updates (or use WebSocket for true real-time)
        const statusResponse = await fetch(
          `${process.env.DJANGO_API_URL}/v1/data_files/${params.id}`,
          { headers: { Cookie: request.headers.get('cookie') || '' } }
        )
        const data = await statusResponse.json()

        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify(data)}\n\n`)
        )

        // Wait 2 seconds before polling again
        await new Promise(resolve => setTimeout(resolve, 2000))
      }
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
}
```

**Note:** SSE support is a post-MVP enhancement and is not required for the initial 8-week delivery.

### Workflow-to-Pattern Mapping

| Workflow | Primary Read Pattern | Primary Write Pattern | Notes |
|----------|----------------------|-----------------------|-------|
| **User management** | Server-rendered list/detail pages with filterable queries | Dedicated approval/update endpoints through Django | Avoid generic client-side user editing flows for approval-heavy operations |
| **Data file submission review** | Server-rendered list plus detail pages with aggregated status metadata | Explicit reparse and state-transition endpoints | Good fit for thin BFF shaping because list/detail views often need aggregated status |
| **Parsed record inspection** | Server-side pagination with optional cursor model | Mostly read-only; export endpoints for bulk actions | Strongest justification for SSR/RSC because datasets are large and filter-heavy |
| **Error report viewing** | Server-rendered tables with server-side filtering and downloadable artifacts | Usually read-only; regenerate/report actions should be dedicated endpoints | Prefer streamed downloads over building large client-side blobs |
| **Feature flag management** | Server-rendered list and detail views | Restricted mutation endpoints with audit logging | Must preserve strong authorization and audit visibility |
| **Audit log viewing** | Read-heavy server-rendered tables with server-side filtering | Typically no write path | Good candidate for initial migration because it is read-heavy and low-risk |

---

## Authentication & Authorization

### Authentication Strategy

**Approach:** Reuse existing Django authentication infrastructure (session-based via Login.gov/AMS OIDC)

**Recommendation:** Do not introduce a second session authority such as NextAuth for the initial implementation. The admin app should treat Django as the authoritative session and permission source, and use middleware plus server-side checks to validate that session.

**Optional Future Path:** If TDP later needs multiple independently deployed frontends and services to participate in a broader shared SSO model, Keycloak can be evaluated as an identity broker or federation layer. That should be a separate initiative, because it changes platform ownership, operational complexity, and migration sequencing. It is not required to deliver the React admin console.

### Session Flow

```
1. Admin User visits /admin
   ↓
2. Next.js middleware checks for Django session cookie
   ↓
   [Cookie present?] ─→ YES ─→ Validate with Django → Grant access
   ↓
   NO
   ↓
   Redirect to Login.gov OIDC endpoint (via existing backend)
   ↓
3. User authenticates at Login.gov
   ↓
4. Django backend validates OIDC token, sets encrypted session cookie
   ↓
5. Redirect back to /admin with session cookie
   ↓
6. Next.js middleware validates session cookie
   ↓
7. Admin console renders
```

### Implementation Details

**Next.js Middleware Authentication:**

```typescript
// middleware.ts
import { NextRequest, NextResponse } from 'next/server'

export async function middleware(request: NextRequest) {
  // Check for Django session cookie
  const sessionCookie = request.cookies.get('sessionid')
  
  if (!sessionCookie) {
    // No session → redirect to login
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Validate session with Django backend
  const sessionValid = await validateDjangoSession(sessionCookie.value)
  
  if (!sessionValid) {
    // Invalid session → redirect to login
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Session valid → continue to admin page
  return NextResponse.next()
}

async function validateDjangoSession(sessionId: string): Promise<boolean> {
  try {
    const response = await fetch(
      `${process.env.DJANGO_API_URL}/v1/auth_check`,
      {
        headers: {
          'Cookie': `sessionid=${sessionId}`,
        },
      }
    )
    return response.status === 200
  } catch {
    return false
  }
}

export const config = {
  matcher: ['/admin/:path*'],
}
```

**CSRF Strategy for Mutating Requests:**

Because the recommended design relies on cookie-authenticated requests to Django, the implementation must define CSRF handling explicitly. The baseline approach should be:

1. Next.js reads the Django-issued CSRF cookie on the incoming request.
2. Mutating BFF requests forward the CSRF token to Django using the expected header.
3. Django remains the final CSRF enforcement point.
4. SameSite cookie settings and trusted origins must be aligned across admin and backend domains.

If the deployment topology uses separate subdomains for admin and API, the cookie domain, CSRF trusted origins, and CORS posture must be documented and tested together.

**Admin Role Validation:**

```typescript
// lib/auth.ts
export async function getAdminUser(request: NextRequest) {
  const response = await fetch(
    `${process.env.DJANGO_API_URL}/v1/auth_check`,
    {
      headers: {
        'Cookie': request.headers.get('cookie') || '',
      },
    }
  )

  if (!response.ok) return null

  const userData = await response.json()
  
  // Check admin role
  if (!userData.is_admin) {
    throw new Error('User is not an admin')
  }

  return userData
}
```

### Authorization Strategy

**Approach:** Role-based access control (RBAC) via Django admin role check

| Permission Model | Implementation |
|-----------------|----------------|
| **Admin Role Check** | `user.is_admin` flag from Django User model |
| **Per-Resource Authorization** | BFF layer checks object-level permissions (e.g., STT-scope for reviewer roles) |
| **Feature Flag Permissions** | Only superusers can edit feature flags (enforced in BFF + Django backend) |

### Authorization Model by Layer

| Layer | Responsibility |
|------|----------------|
| **Next.js route protection** | Prevent non-admin users from reaching admin pages and hide inaccessible routes |
| **BFF route handlers** | Shape requests, perform coarse authorization checks, and forward authenticated requests |
| **Django backend** | Final enforcement of permissions, workflow rules, audit logging, and mutation rules |

The rule of thumb is that Next.js may improve UX and reduce unnecessary backend calls, but Django must remain the final enforcement layer for anything security-sensitive.

**Example: STT-scoped reviewer role**

```typescript
// BFF: app/api/users/[id]/route.ts
export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await getAdminUser(request)
  
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const targetUser = await fetchUser(params.id)

  // Authorization: Admin OR STT-scoped reviewer for same STT
  const canEdit = user.is_admin || 
    (user.is_reviewer && user.stt_id === targetUser.stt_id)

  if (!canEdit) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
  }

  // Proceed with update...
}
```

### Session Timeout & Idle Detection

- Reuse existing Django session timeout (default: 12 hours)
- Optional: Add client-side idle timer that redirects to login after period of inactivity
- Implement graceful session expiration feedback (toast notification → redirect)

---

## API Integration Strategy

### BFF (Backend for Frontend) Layer Rationale

**Why a BFF layer?**

1. **Request Aggregation:** Admin workflows often need data from multiple Django endpoints joined together
   - Example: User list with change request count per user
   - Example: File submission with latest parse status + error summary

2. **Response Transformation:** Django REST API returns generic structures; admin needs domain-specific shapes
   - Example: Flatten nested objects for table display
   - Example: Compute derived fields (e.g., "days since submission")

3. **Authorization & Filtering:** Server-side enforce admin-specific rules
   - Example: STT-scoped reviewers see only their STT's submissions
   - Example: Audit log filtering by accessible resources

4. **Rate Limiting & Caching:** Centralized control of backend traffic
   - Example: Heavily-filtered audit log queries cached for 1 hour
   - Example: Rate-limit large exports to prevent DoS

### API Architecture

The BFF runs as Next.js API routes and communicates with Django backend via HTTP (same docker network in Cloud.gov).

```
Request Flow:

Admin Browser
    ↓ HTTPS
React Admin Console (Next.js)
    ↓ HTTP (internal docker network)
BFF Layer (Next.js API routes)
  ↓ HTTP (internal app-to-app calls)
Django Backend
    ↓
PostgreSQL Database
```

### Recommended API Boundary

The recommended order of preference is:

1. **Reuse existing Django REST endpoints where possible.**
2. **Add admin-specific Django endpoints when a workflow is not well modeled as generic CRUD.**
3. **Use a Next.js BFF only for response shaping, aggregation, pagination adaptation, and route-level orchestration.**
4. **Avoid direct database access from Next.js in the MVP.**

This keeps business logic close to the existing domain model and prevents drift between Python and Node implementations.

### How Next.js Accesses Data

In the recommended architecture, Next.js does not directly connect to PostgreSQL for normal application behavior.

The expected data path is:

`Browser -> Next.js admin app -> Django API -> PostgreSQL`

That means:

1. The browser requests an admin page from the Next.js application.
2. A Next.js Server Component or route handler fetches data from Django.
3. Django applies authentication, authorization, workflow rules, and query logic.
4. Django reads from or writes to PostgreSQL.
5. Django returns the result to Next.js.
6. Next.js renders HTML on the server or returns shaped data to the browser.

Next.js may still include a thin BFF layer for page-specific response shaping, aggregation, pagination adaptation, and route orchestration, but that BFF should call Django-owned endpoints rather than query the database directly.

This separation is important for TDP because Django already owns:

- authentication and session handling
- permission checks
- audit logging
- workflow enforcement, including actions such as reparse
- domain validation and mutation rules

If Next.js were to connect directly to the database for normal admin behavior, the implementation would risk duplicating business rules and creating drift between the Node.js and Django layers.

Direct database access from Next.js should therefore be treated as an exception case only, such as a narrowly scoped read-only reporting use case, and should require explicit review, read-only credentials, and a separate architecture decision.

### BFF Endpoint Design

**Proxy endpoints** (minimal transformation):
```typescript
// GET /api/feature-flags → proxy to GET /v1/feature_flags
// POST /api/feature-flags → proxy to POST /v1/feature_flags
```

**Custom aggregation endpoints**:
```typescript
// GET /api/admin/dashboard → aggregates multiple Django endpoints
// Response combines:
//   - Recent submissions (from /v1/data_files)
//   - Pending approvals (from /v1/users/change_requests)
//   - Active parsing jobs (from /v1/data_files with filter)
```

**Custom mutation endpoints**:
```typescript
// POST /api/submissions/[id]/reparse → custom workflow
//   1. Validate current state
//   2. Update DataFile.parsing_state
//   3. Queue parse task
//   4. Emit audit log
//   5. Send notification email (optional)
```

### Calling Django REST API from BFF

**Authentication:**
- Include Django session cookie from request to BFF
- BFF forwards cookie to Django backend

```typescript
// BFF helper
async function callDjangoAPI(
  path: string,
  request: NextRequest,
  options: RequestInit = {}
) {
  const url = `${process.env.DJANGO_API_URL}${path}`
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      // Forward session cookie
      'Cookie': request.headers.get('cookie') || '',
    },
  })

  if (response.status === 401) {
    // Session expired → client will redirect to login
    throw new Error('Unauthorized')
  }

  return response
}
```

### Handling Large Result Sets

**Challenge:** Parsed records table may have 100k+ rows; can't load all client-side.

**Solution: Server-side pagination with cursor**

```typescript
// BFF: GET /api/records
export async function GET(request: NextRequest) {
  const searchParams = new URL(request.url).searchParams
  const query = searchParams.get('q')
  const cursor = searchParams.get('cursor')
  const limit = 100

  const response = await callDjangoAPI(
    `/v1/parsed_records?search=${query}&cursor=${cursor}&limit=${limit + 1}`,
    request
  )
  
  const allRecords = await response.json()
  
  // Detect if more results exist
  const hasMore = allRecords.length > limit
  const records = allRecords.slice(0, limit)
  
  return NextResponse.json({
    records,
    hasMore,
    nextCursor: hasMore ? records[records.length - 1].id : null,
  })
}
```

---

## Rendering Strategy

### When to Use Each Pattern

| Scenario | Pattern | Rationale |
|----------|---------|-----------|
| List pages (users, files, logs) | Server Component + SSR | Data loaded server-side; no client JS needed |
| Real-time filters (search box) | Client Component with Suspense | URL updates → Server Component re-renders |
| Modal dialogs, toggles | Client Component | Client-side state (open/close) |
| Data grid with sorting/pagination | Hybrid (Server Component + Client interactivity) | Server-side pagination; client-side UI controls |
| File downloads/exports | BFF + streaming response | Prevent large payloads in browser |

### Streaming & Progressive Enhancement

**Server Component Streaming:**

```typescript
// app/admin/dashboard/page.tsx
import { Suspense } from 'react'
import DashboardSummary from './_components/DashboardSummary'
import DashboardSummarySkeleton from './_components/DashboardSummarySkeleton'
import RecentSubmissions from './_components/RecentSubmissions'
import RecentSubmissionsSkeleton from './_components/RecentSubmissionsSkeleton'

export default async function DashboardPage() {
  return (
    <div>
      <h1>Admin Dashboard</h1>
      
      {/* Suspense boundaries allow independent streaming */}
      <Suspense fallback={<DashboardSummarySkeleton />}>
        <DashboardSummary />
      </Suspense>

      <Suspense fallback={<RecentSubmissionsSkeleton />}>
        <RecentSubmissions />
      </Suspense>
    </div>
  )
}
```

**Browser receives:**
1. HTML skeleton (fast)
2. Summary component streams in (1st)
3. Recent submissions component streams in (2nd)

**Perceived performance:** Page becomes interactive much faster than traditional client-side rendering.

### Performance Considerations

**Cache Strategy:**
- Use `revalidate` option on fetch calls to control cache duration
- Example: Dashboard summary cached for 1 minute; detailed tables cached for 5 minutes

```typescript
// Cache for 60 seconds before re-fetching
const data = await fetch(url, {
  next: { revalidate: 60 },
})
```

**Image Optimization:**
- Use Next.js `<Image>` component with automatic optimization
- Export CSV/PDF reports as attachment downloads (not rendered in browser)

---

## Deployment Topology

### Current Infrastructure

```
Cloud.gov Foundation
├── Organization: "tanfdata"
├── Space: "prod" | "staging" | "dev"
└── Applications:
    ├── tdp-frontend (CRA) → port 3000
    ├── tdp-backend (Django) → port 8080
    └── [NEW] tdp-admin (Next.js) → port 3001
```

  ### How This Fits the Existing TDP Stack

  TDP production already runs with a split frontend/backend model in Cloud.gov:

  1. `tdp-frontend` serves the current CRA application.
  2. `tdp-backend` serves Django and the REST API.

  The recommended standalone Next.js admin console fits this pattern naturally by becoming a third application:

  3. `tdp-admin` serves the admin-only React application.

  That means the recommended architecture is an extension of the current deployment model, not a fundamental change to it. The stack would become:

  - `tdp-frontend`: public user-facing experience
  - `tdp-admin`: admin-facing experience
  - `tdp-backend`: shared system-of-record API, auth, permissions, workflow rules, and persistence

  ### Do We Need Another Cloud.gov App?

  **If the team accepts the standalone Next.js recommendation, yes.**

  You would add a third Cloud.gov app for the admin UI because Next.js needs its own runtime, build artifact, and deployment lifecycle. In that model:

  - `tdp-frontend` remains the CRA user app
  - `tdp-admin` is a new Next.js admin app
  - `tdp-backend` remains the Django backend/API app

  **If the team instead chooses to add admin routes into the existing CRA frontend, no.**

  In that alternative, there is no third Cloud.gov app. Admin pages are bundled into `tdp-frontend`, and both user and admin routes are served by the same frontend deployment.

  ### Recommendation in Cloud.gov Terms

  Because TDP already operates separate frontend and backend apps, a standalone `tdp-admin` app is operationally consistent with the current platform model. It adds one more deployable unit, but it preserves the separation of concerns that already exists in production.

  This is the practical deployment tradeoff:

  - **Standalone Next.js admin:** one additional Cloud.gov app, cleaner isolation, independent deploys, better fit for SSR/RSC
  - **CRA-integrated admin:** no additional Cloud.gov app, but admin and user experiences become tightly coupled in one frontend deployment

### Proposed Deployment

**Service Architecture:**

```
┌─────────────────────────────────────────┐
│         Cloud.gov Foundation            │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐   ┌──────────┐           │
│  │  Router  │   │  Router  │           │
│  │(Frontend)│   │ (Admin)  │           │
│  └────┬─────┘   └────┬─────┘           │
│       │              │                 │
│  ┌────▼─────────────▼──────┐          │
│  │ Kong/Route53 (Optional) │          │
│  │ api.example.gov         │          │
│  │ admin.example.gov       │          │
│  └────┬──────────────────┬─┘          │
│       │                  │             │
│  ┌────▼─────┐      ┌─────▼────┐      │
│  │ Frontend  │      │  Admin   │      │
│  │ Container │      │Container │      │
│  │ (CRA)     │      │(Next.js) │      │
│  │ :3000     │      │ :3001    │      │
│  └────┬─────┘      └─────┬────┘      │
│       │                  │             │
│       └──────────┬───────┘             │
│                  │                     │
│  ┌───────────────▼───────────────┐   │
│  │ Backend Container             │   │
│  │ (Django + DRF)                │   │
│  │ :8080                         │   │
│  └───────────────┬───────────────┘   │
│                  │                     │
│  ┌───────────────▼───────────────┐   │
│  │ PostgreSQL Service            │   │
│  │ (Managed database)            │   │
│  └───────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### Deployment Configuration

**manifest.yml for Admin Console:**

```yaml
---
version: 1
applications:
- name: tdp-admin
  instances: 2
  memory: 512M
  disk_quota: 2G
  timeout: 180
  command: npm run start
  buildpacks:
    - nodejs_buildpack
  env:
    NODE_ENV: production
    DJANGO_API_URL: http://tdp-backend:8080
    ADMIN_PUBLIC_URL: https://admin.example.gov
    DJANGO_AUTH_CHECK_PATH: /v1/auth_check
  health-check-type: process
  health-check-timeout: 60
  health-check-invocation-timeout: 60
```

### Environment Configuration

**Environment Variables (per deployment):**

| Variable | Dev | Staging | Prod | Notes |
|----------|-----|---------|------|-------|
| `NODE_ENV` | development | production | production | Next.js optimization level |
| `DJANGO_API_URL` | http://tdp-backend:8080 | http://tdp-backend:8080 | http://tdp-backend:8080 | Internal docker network |
| `ADMIN_PUBLIC_URL` | http://localhost:3001 | https://admin-staging.example.gov | https://admin.example.gov | Public base URL for redirects and links |
| `DJANGO_AUTH_CHECK_PATH` | /v1/auth_check | /v1/auth_check | /v1/auth_check | Session validation endpoint |
| `LOG_LEVEL` | debug | info | info | Logging verbosity |
| `ENABLE_PROFILING` | true | false | false | Performance profiling |

### Scaling & Performance

**Initial Configuration:**
- 2 instances of Next.js (load-balanced)
- 512M memory per instance (reasonable for Node.js app; adjust based on metrics)
- Local SSD for `next/cache` (Next.js ISR cache) — **Note:** Cloud.gov ephemeral filesystem; cache resets on deploys

**Monitoring & Alerts:**
- Add metrics through custom instrumentation, an exporter library, or platform-compatible log-derived metrics. Do not assume native Prometheus support from Next.js itself.
- Track:
  - `next_http_request_duration_seconds` (API response time)
  - `nodejs_heap_size_bytes` (memory usage)
  - `http_requests_total` (throughput)
  - Django API error rates (4xx, 5xx)

### Cloud.gov Considerations

1. **Route topology:** Use a dedicated admin route such as `admin.<domain>` or `/admin` behind the edge router, but keep backend routes private where possible.
2. **Internal networking:** Prefer app-to-app communication between `tdp-admin` and `tdp-backend` over exposing additional public backend surfaces.
3. **Ephemeral filesystem:** Do not rely on local disk for persistent exports, uploaded artifacts, or durable cache behavior.
4. **Operational observability:** Route logs and metrics into the same operational monitoring strategy already used for frontend and backend apps.
5. **Blue/green or rolling deploys:** Keep admin deployment independent so operational issues in admin do not force rollback of the user-facing frontend.

### Recommended Production Topology

For TDP's current Cloud.gov setup, the recommended production topology is:

`Admin Browser -> tdp-admin -> tdp-backend -> PostgreSQL`

in parallel with:

`User Browser -> tdp-frontend -> tdp-backend -> PostgreSQL`

This keeps the backend shared, while separating the user-facing and admin-facing web runtimes.

**CDN Caching (Optional):**
- Static assets (`_next/static`) → CDN with long cache TTL (1 year, hash-based invalidation)
- HTML pages (RSC output) → CDN with short TTL (1 minute) or disable caching for dynamic content

---

## Code Sharing Strategy

### Option 1: Monorepo with Shared Package (Recommended)

**Structure:**

```
/TANF-app
├── packages/
│   ├── ui-components/          # Shared USWDS + custom components
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Table.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   └── ...
│   │   │   ├── hooks/
│   │   │   │   ├── useTableState.ts
│   │   │   │   └── usePagination.ts
│   │   │   ├── types/
│   │   │   │   └── index.ts       # Shared TypeScript types
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── api-client/              # Shared API client logic
│   │   ├── src/
│   │   │   ├── client.ts         # Fetch wrapper
│   │   │   ├── types.ts          # API request/response types
│   │   │   └── errors.ts         # Error handling
│   │   ├── package.json
│   │   └── tsconfig.json
│
├── tdrs-frontend/               # Existing CRA app
│   ├── src/
│   ├── package.json
│   └── tsconfig.json
│
├── tdrs-admin/                  # New Next.js admin app
│   ├── app/
│   ├── lib/
│   ├── package.json
│   └── tsconfig.json
│
└── package.json (root)          # Workspace root
```

**Root package.json (Yarn workspaces):**

```json
{
  "name": "tdp-workspace",
  "private": true,
  "packageManager": "yarn@4.6.0",
  "workspaces": [
    "packages/*",
    "tdrs-frontend",
    "tdrs-admin"
  ]
}
```

**Usage in both apps:**

```typescript
// tdrs-frontend or tdrs-admin
import { Button, Table } from '@tdp/ui-components'
import { apiClient, type User } from '@tdp/api-client'
```

**Advantages:**
- Single dependency resolution (yarn workspaces)
- Shared components evolve together
- Types are synchronized
- Both apps can import from packages

**Disadvantages:**
- Requires coordinated deploys if packages change
- Version conflicts possible (though rare with single workspace)

---

### Option 2: Separate Repositories (Alternative)

If monorepo is rejected, publish shared packages to private npm registry (GitHub Packages, Verdaccio, etc.).

```
github.com/raft-tech/tdp-ui-components (separate repo)
github.com/raft-tech/tdp-api-client (separate repo)
github.com/raft-tech/TANF-app (main repo)
  - tdrs-frontend/
  - tdrs-admin/
```

**Trade-offs:**
- Advantage: cleaner separation; can publish components as public library
- Cost: version management overhead; requires versioning/tagging
- Cost: slower feedback loop during development

**Recommendation:** Start with Option 1 (monorepo). Can extract to separate repos later if components mature and need independent versioning.

---

## Large Dataset Handling

### Challenge: Rendering Thousands of Records

Example: Parsed records table for a single submission might contain 10,000–100,000+ rows.

Traditional client-side rendering (load all rows, render table in browser) hits memory limits and causes jank.

### Solution: Server-Side Pagination + RSC Streaming

**Step 1: Server Component fetches one page**

```typescript
// app/admin/records/page.tsx
async function RecordsPage({ searchParams }) {
  const page = parseInt(searchParams.page || '1', 10)
  const pageSize = 100
  
  // Fetch exactly one page from BFF
  const records = await fetchRecordsPage({
    page,
    limit: pageSize,
    search: searchParams.q,
  })

  return <RecordsTable records={records} page={page} pageSize={pageSize} />
}
```

**Step 2: BFF handles pagination**

```typescript
// app/api/records/route.ts
export async function GET(request: NextRequest) {
  const page = parseInt(new URL(request.url).searchParams.get('page') || '1', 10)
  const pageSize = 100
  const offset = (page - 1) * pageSize

  // Call Django backend with offset/limit
  const response = await callDjangoAPI(
    `/v1/parsed_records?offset=${offset}&limit=${pageSize}`,
    request
  )

  return response // Django returns page + total count
}
```

**Step 3: Client-side pagination controls**

```typescript
// Client Component (embedded in Server Component)
'use client'

import Link from 'next/link'

export function RecordsPaginator({ page, totalPages, searchParams }) {
  return (
    <nav>
      {page > 1 && (
        <Link href={`?page=${page - 1}&${searchParams}`}>← Previous</Link>
      )}
      
      <span>Page {page} of {totalPages}</span>
      
      {page < totalPages && (
        <Link href={`?page=${page + 1}&${searchParams}`}>Next →</Link>
      )}
    </nav>
  )
}
```

### Optimization: Cursor-Based Pagination (for >100k rows)

Offset-based pagination becomes slow at large offsets (database needs to scan all rows before returning). Cursor-based is faster.

```typescript
// BFF: GET /api/records?cursor=eyJpZCI6IDk5OTl9
export async function GET(request: NextRequest) {
  const cursor = new URL(request.url).searchParams.get('cursor')
  const pageSize = 100

  let query = `/v1/parsed_records?limit=${pageSize + 1}` // Fetch extra to detect "more"
  
  if (cursor) {
    const decoded = JSON.parse(Buffer.from(cursor, 'base64').toString())
    query += `&after_id=${decoded.id}`
  }

  const records = await callDjangoAPI(query, request)
  
  const hasMore = records.length > pageSize
  const pageRecords = records.slice(0, pageSize)
  
  const nextCursor = hasMore
    ? Buffer.from(JSON.stringify({ id: pageRecords[pageRecords.length - 1].id })).toString('base64')
    : null

  return NextResponse.json({ records: pageRecords, nextCursor, hasMore })
}
```

### Optimization: Column Virtualization (optional, post-MVP)

For tables with many columns (20+), render only visible columns:

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'

export function LargeRecordsTable({ records, columns }) {
  const columnVirtualizer = useVirtualizer({
    count: columns.length,
    getScrollElement: () => scrollContainerRef.current,
    estimateSize: () => 100, // pixel width per column
    overscan: 5, // render 5 columns beyond visible area
  })

  return (
    <table>
      <thead>
        <tr>
          {columnVirtualizer.getVirtualItems().map(virtualColumn => (
            <th key={virtualColumn.index}>
              {columns[virtualColumn.index].label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {records.map(record => (
          <tr key={record.id}>
            {columnVirtualizer.getVirtualItems().map(virtualColumn => (
              <td key={`${record.id}-${virtualColumn.index}`}>
                {record[columns[virtualColumn.index].key]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
```

**Note:** Column virtualization is likely overkill for the initial 8-week MVP; focus on page-based pagination first.

---

## Migration Strategy

### Delivery Assumption

The plan below assumes a hard implementation window of 8 weeks and therefore prioritizes a credible MVP over full Django admin parity.

### Recommended MVP Scope for an 8-Week Window

The first release should target the workflows with the best value-to-complexity ratio:

- Feature flag management
- Audit log viewing
- User list and limited approval/review flows
- Data file submission review and reparse trigger

The following should be explicitly deferred unless staffing is materially larger than assumed:

- Full parsed-record browser parity
- Rich error-report exploration across very large datasets
- Real-time updates or SSE
- Advanced export/report generation
- Full Django admin deprecation

### Week 1: Foundation and Deployment Skeleton

**Goals:**
- Stand up the Next.js admin app
- Establish Cloud.gov deployment path
- Validate Django session reuse and route protection

**Deliverables:**
- `tdp-admin` project scaffold
- Cloud.gov manifest and deployment pipeline
- Middleware-based session validation against Django
- Base admin shell, navigation, layout, and authorization guard

### Weeks 2-3: Low-Risk Read-Heavy Workflows

**Goals:**
- Deliver fast, read-heavy workflows first to validate page structure, auth, and API access patterns

**Deliverables:**
- Audit log list view
- Feature flag list and detail views
- Basic filtering, sorting, pagination, and loading/error states
- Shared table and form primitives aligned with USWDS

### Weeks 4-5: User Management MVP

**Goals:**
- Deliver the minimum viable user-management surface needed by operations

**Deliverables:**
- User list view with filtering
- User detail/review surface
- Approval and limited change-request actions
- Audit logging integration for mutations

**Scope Control:**
- Favor review and approval workflows over full user-admin parity
- Defer rarely used editing paths unless they are essential to release

### Weeks 6-7: Submission Review MVP

**Goals:**
- Cover the most important domain-specific admin workflow that Django admin handles poorly today

**Deliverables:**
- Data file list and detail pages
- Parse status display and summary metadata
- Reparse trigger flow with confirmation and audit trail
- Error summary display at the file level, not full record-browser parity

### Week 8: Hardening and Launch Readiness

**Goals:**
- Stabilize the MVP, close operational gaps, and prepare for production rollout

**Deliverables:**
- Regression fixes and accessibility pass
- Monitoring, logging, and alerting hooks
- Deployment runbook and rollback plan
- Documentation for support and operations teams

### Post-MVP Backlog

The following should be documented as the first post-launch increment rather than implied to fit within the initial 8-week delivery:

- Parsed-record browser with server-side pagination/cursor support
- Deep error-report investigation views
- Export/report generation beyond basic file-level downloads
- Live status updates
- Full retirement of Django admin views

---

## Risks & Mitigation

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **Performance regression on large submissions** | High | Keep the MVP at file-level summaries and paginated lists first; validate large-dataset patterns before committing to full parsed-record parity |
| **Session timeout UX issues** | Medium | Implement graceful logout + idle timer; test edge cases (tab switching, etc.) |
| **BFF becomes bottleneck** | Medium | Monitor API response times; implement caching layer (HTTP cache headers) |
| **Django API stability** | Medium | Admin console depends on Django backend; ensure backend reliability + redundancy |
| **USWDS component mismatch** | Low | Use official USWDS React library; validate accessibility with Pa11y in CI |
| **Too many shared packages (scope creep)** | Medium | Strict code review; shared packages only after 2+ consumers |
| **Complexity in auth/RBAC** | Medium | Document auth flows thoroughly; test edge cases (session expiry, permission changes) |

---

## Open Questions & Decisions

### Q1: Should we use GraphQL instead of REST BFF?

**Answer:** No, stick with REST for the initial MVP.

**Rationale:**
- Django backend uses REST; adding GraphQL layer adds complexity
- REST + Server Components handling query aggregation is sufficient
- GraphQL can be evaluated later if BFF becomes bottleneck

---

### Q2: Multi-tenancy: Should admins from different STTs have separate admin consoles?

**Answer:** No, single unified admin console; authorization via role checks in BFF.

**Rationale:**
- Reduces deployment complexity
- Easier to enforce org-wide policies
- STT-scoped admins see only their STT (BFF-side filtering)

---

### Q3: CSR vs SSR vs ISR for dashboard?

**Answer:** ISR (Incremental Static Regeneration) + on-demand revalidation.

```typescript
// Revalidate dashboard every 5 minutes (or on-demand)
export const revalidate = 300 // seconds

// In mutation handler, trigger revalidation
revalidateTag('dashboard')
```

---

### Q4: How to handle long-running operations (e.g., bulk export)?

**Answer:** Server Action + background job queue.

```typescript
// BFF: POST /api/submissions/bulk-export
export async function POST(request: NextRequest) {
  const ids = await request.json()
  
  // Queue async job
  const jobId = await queueExportJob(ids)
  
  // Return job status URL
  return NextResponse.json({ jobId, statusUrl: `/api/jobs/${jobId}` })
}

// Client polls: GET /api/jobs/{jobId}
// Returns: { status: 'pending' | 'complete' | 'failed', downloadUrl?: string }
```

---

### Q5: Should we prebuild static pages?

**Answer:** No, build on-demand for admin pages.

**Rationale:**
- Admin pages are data-driven (user list, file submissions); static generation not applicable
- Dynamic rendering with appropriate caching is simpler

---

### Q6: How to share Dockerfile between frontend and admin?

**Answer:** Use multi-stage Dockerfile in each app; consider Node.js base image optimization later.

---

## Appendix

### A. Comparison: Django Admin vs. React Admin

| Feature | Django Admin | React Admin (Proposed) | Notes |
|---------|-------------|----------------------|-------|
| **Time to Build** | Fast (built-in) | Slower (custom) | React requires explicit component building |
| **Performance** | Adequate for <1k rows | Optimized for 100k+ rows | RSC + pagination handles scale |
| **Customization** | Limited (template-based) | Unlimited (React) | React provides full control |
| **Accessibility** | Manual USWDS retrofit | Native USWDS | Easier compliance in React |
| **Mobile Responsiveness** | Limited | Full (Next.js responsive) | Mobile admin useful for field operations |
| **State Management** | Session + URL params | URL params + Client state | Less coupling to Django patterns |

### B. Technology Versions (Baseline)

- **Node.js:** 18+ LTS
- **Next.js:** 14+ (App Router, RSC stable)
- **React:** 18.2+
- **USWDS:** 6.0+
- **TypeScript:** 5.0+
- **Yarn:** 4.6.0

### C. Further Reading

- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [React Server Components RFC](https://github.com/reactjs/rfcs/blob/main/text/0188-server-components.md)
- [USWDS React Components](https://senior-sass.github.io/react-uswds/)
- [Django Session Authentication](https://docs.djangoproject.com/en/stable/topics/auth/)
- [Cloud Foundry Application Manifest](https://docs.cloudfoundry.org/devguide/deploy-apps/manifest-attributes.html)

---

## Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| **Tech Lead** | [To be filled] | | Pending |
| **Product Owner** | [To be filled] | | Pending |
| **DevOps Lead** | [To be filled] | | Pending |

---

**Document Version:** 1.0  
**Last Updated:** April 2026  
**Next Review Date:** After MVP scope sign-off or immediately before implementation kickoff
