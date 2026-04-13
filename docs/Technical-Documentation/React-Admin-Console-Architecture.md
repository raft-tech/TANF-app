# React Admin Console: High-Level Architecture Specification

**Issue:** #5746  
**Status:** Draft for Architecture Review  
**Date:** April 2026  
**Audience:** Engineering, Technical Leadership, DevOps

---

## Table of Contents

- [React Admin Console: High-Level Architecture Specification](#react-admin-console-high-level-architecture-specification)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [Scope](#scope)
  - [Principles](#principles)
  - [High-Level Component Architecture](#high-level-component-architecture)
  - [System Boundaries and Data Access](#system-boundaries-and-data-access)
    - [BFF shaping vs. pass-through pattern](#bff-shaping-vs-pass-through-pattern)
  - [Authentication and Authorization](#authentication-and-authorization)
    - [Authentication model](#authentication-model)
    - [Authorization model](#authorization-model)
    - [CSRF and cookie posture](#csrf-and-cookie-posture)
    - [Session validation flow](#session-validation-flow)
  - [Rendering and Interaction Model](#rendering-and-interaction-model)
  - [Technology Stack](#technology-stack)
  - [Deployment Topology (Cloud.gov)](#deployment-topology-cloudgov)
  - [Migration Strategy](#migration-strategy)
  - [Phasing Principles](#phasing-principles)
  - [Risks and Mitigations](#risks-and-mitigations)

---

## Executive Summary

This document defines the target architecture for replacing Django admin workflows with a React-based admin console while keeping Django as the system-of-record backend. For the decision rationale (CRA vs. Next.js, motivations for moving away from Django admin), see [ADR-023: React Admin Console — CRA vs. Next.js](Architecture-Decision-Record/023-react-admin-console.md).

The architecture is a standalone Next.js admin application that:

- uses server-side rendering and server components for data-heavy admin workflows,
- reuses existing Django session/auth infrastructure,
- keeps business rules, authorization enforcement, workflow transitions, and audit behavior in Django,
- is deployed as a separate Cloud.gov app alongside the existing user frontend and backend.

Core workflows this architecture must support:

- user access and account-change review workflows,
- data file submission review and reparse initiation,
- parsed record inspection and error report viewing,
- feature flag administration,
- audit log review and filtering.

---

## Scope

This is an architecture specification. It describes system structure, boundaries, key design choices, and critical integration patterns.

---

## Principles

1. Django remains authoritative for domain and security decisions.
2. Next.js is a presentation/orchestration layer, not a replacement backend.
3. Prefer API reuse over policy duplication.
4. Use BFF behavior only where it adds clear admin UX value.

---

## High-Level Component Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                          Admin Browser                           │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     tdp-admin (Next.js)                         │
│  - SSR/RSC rendering                                             │
│  - admin route protection                                        │
│  - optional thin BFF shaping                                     │
│  - USWDS-based admin UI                                          │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     tdp-backend (Django)                        │
│  - auth/session validation                                       │
│  - authorization + workflow rules                                │
│  - audit logging                                                 │
│  - REST API and business logic                                   │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                         PostgreSQL                               │
└──────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                          User Browser                            │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    tdp-frontend (Current CRA)                    │
│                     user-facing routes                           │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     tdp-backend (Django)                         │
└──────────────────────────────────────────────────────────────────┘
```

This reflects the target coexistence model: existing CRA user app remains, while admin moves to a dedicated Next.js runtime.

---

## System Boundaries and Data Access

Expected request path for admin workflows:

Browser → Next.js admin → Django API → PostgreSQL

Boundary rules:

- Next.js can shape or aggregate responses for admin views.
- Django owns permission checks, workflow transitions, and domain validation.
- Direct database access from Next.js is out of scope.
- Any exception to direct DB access requires separate architecture review.

Data access patterns by workflow:

- Read-heavy pages (lists/tables): server-rendered with server-side filtering and pagination.
- Workflow mutations (approve/reparse/update flags): explicit mutation endpoints with Django-side audit and policy enforcement.
- Large dataset navigation: paginated or cursor-based API interactions, not client-side bulk loading.

### BFF shaping vs. pass-through pattern

Most admin screens should use **pass-through** — the Next.js server component calls a single Django endpoint and renders the response directly.

```
// Pass-through example: fetch one Django endpoint and render the response.
fetch(`${BACKEND_URL}/api/admin/users/?page=1&status=approved`, reqOpts)
```

Use **BFF shaping** only when an admin view requires data from multiple Django endpoints that should be composed before rendering.

```
// BFF shaping example: compose multiple Django responses for one admin view.
Promise.all([
  fetch(`${BACKEND_URL}/api/admin/submissions/${id}/`, reqOpts),
  fetch(`${BACKEND_URL}/api/admin/submissions/${id}/errors/`, reqOpts),
])
```

The rule of thumb: if a single Django endpoint can serve the view, pass-through. If the view needs to join data that Django doesn't serve in a single response, use BFF shaping — but do not add business logic or authorization checks in the BFF layer.

---

## Authentication and Authorization

### Authentication model

- Reuse existing Django session-based authentication.
- Next.js validates session presence and validity for admin routes.
- No second session authority is introduced for MVP.

### Authorization model

- Route-level UX gating in Next.js is allowed for user experience.
- Final authorization enforcement is always in Django.
- Object-level and workflow-level checks remain backend-owned.

### CSRF and cookie posture

- Cookie-authenticated mutating calls must carry expected CSRF context.
- Trusted origins, cookie domain attributes, and same-site behavior must be aligned across admin and backend domains.

### Session validation flow

Every admin route validates the session before rendering. The integration works as follows:

```
Admin request
  -> Next.js checks for Django session cookie
  -> Next.js validates session via lightweight Django auth endpoint
  -> invalid session redirects to login
  -> valid session continues to server-rendered admin route
```

For mutations, the CSRF token must be forwarded from the Django-issued cookie:

```
POST admin mutation
  -> forward Django session cookie
  -> include CSRF token in header
  -> Django performs final authz, mutation, and audit logging
```

These examples illustrate the critical auth integration. The flow is pseudocode — exact implementation will depend on cookie domain configuration and session endpoint design.

---

## Rendering and Interaction Model

Rendering strategy mapped to specific admin surfaces:

| Surface | Strategy | Rationale |
|---------|----------|----------|
| User list / Data file list | SSR (server component) | Large paginated datasets; no client state needed |
| User detail / Submission detail | SSR (server component) | Single-entity fetch; render on server |
| Audit log viewer | SSR with streaming | Potentially high-latency queries; progressive render |
| Feature flag toggles | Client component | Immediate local feedback on toggle; mutation via server action |
| Filter/search controls | Client component | Interactive UI; triggers server re-fetch on submit |
| Approval/reparse confirmation modals | Client component | Dialog interaction; form submission via server action |

General rules:

- Default to server components. Only promote to client component when the surface requires browser interactivity (event handlers, local state).
- Server-driven pagination and filtering: pass `page` and filter params as URL search params so server components can fetch the correct slice.
- Avoid client-side bulk loading of large datasets.

---

## Technology Stack

| Area | Choice | Notes |
|------|--------|-------|
| Framework | Next.js 14+ | App Router, SSR/RSC support |
| UI System | USWDS React | Required design/accessibility alignment |
| Forms | React Hook Form + schema validation | Client ergonomics with server-authoritative validation |
| Tables / Data Grid | Server-rendered USWDS tables with backend pagination | Prefer simple tables first; only introduce a heavier grid library if admin workflows prove it necessary |
| Data Fetching | Server-first fetch patterns | Avoid client waterfalls |
| State Management | URL/search-param driven server state plus local component state | Avoid Redux by default for MVP; introduce shared client state only for a concrete cross-page need |
| API Layer | Django REST API with optional thin BFF | Preserve existing backend ownership |
| Testing | Component + integration + E2E | Validate authz, workflow transitions, and admin UX paths |

Tailwind CSS is intentionally excluded from this recommendation. USWDS is the styling system for this architecture.

---

## Deployment Topology (Cloud.gov)

Target runtime model:

- tdp-frontend: existing CRA user app
- tdp-admin: new Next.js admin app
- tdp-backend: shared Django backend and API

Operational implications:

- adds one deployable frontend unit,
- allows admin deployment cadence independent of user-facing frontend,
- preserves backend as shared domain and security boundary.

Cloud.gov considerations:

- prefer internal app-to-app calls from admin to backend,
- treat local filesystem as ephemeral,
- keep observability aligned with existing platform monitoring patterns,
- support rollback strategies without coupling user and admin releases.

---

## Migration Strategy

- Run the existing Django admin and `tdp-admin` in parallel during migration.
- Replace Django admin workflows incrementally, starting with the highest-value read and mutation paths called out in this document.
- Keep Django as the system of record until each replacement workflow is production-validated for authorization, audit behavior, and operational readiness.
- Retire individual Django admin surfaces only after the corresponding React admin workflow is available, stable, and accepted by engineering/product stakeholders.

---

## Phasing Principles

- Auth integration and deployment skeleton come first — all subsequent work depends on a working session flow.
- Read-heavy views (lists, detail pages) before mutation flows — they validate the data-access patterns with lower risk.
- Mutation workflows (approve, reparse) follow once read paths are stable.
- Accessibility verification is continuous, not a final phase — every merged view must pass automated USWDS conformance checks.

---

## Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Performance regressions on large datasets | High | Server-driven pagination and filtering from day one |
| Auth/session edge-case defects | Medium | Explicit session-expiry and CSRF test matrix |
| BFF overgrowth into second backend | Medium | Boundary guardrails in design and review; pass-through as default pattern |
| Operational overhead from third app | Medium | Reuse existing deployment and monitoring practices |
| Accessibility drift | Medium | USWDS conformance plus automated checks in CI |

---

**Document Version:** 3.0  
**Last Updated:** April 2026  
**Related ADR:** [023 — React Admin Console: CRA vs. Next.js](Architecture-Decision-Record/023-react-admin-console.md)  
**Next Review Gate:** Architecture sign-off
