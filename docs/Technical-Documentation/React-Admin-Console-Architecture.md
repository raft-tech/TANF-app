# React Admin Console: High-Level Architecture Specification

**Issue:** #5746  
**Status:** Draft for Architecture Review  
**Date:** April 2026  
**Audience:** Engineering, Technical Leadership, DevOps

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Decision Snapshot (ADR Summary)](#decision-snapshot-adr-summary)
3. [Problem Statement](#problem-statement)
4. [Architecture Scope and Principles](#architecture-scope-and-principles)
5. [High-Level Component Architecture](#high-level-component-architecture)
6. [System Boundaries and Data Access](#system-boundaries-and-data-access)
7. [Authentication and Authorization](#authentication-and-authorization)
8. [Rendering and Interaction Model](#rendering-and-interaction-model)
9. [Technology Stack](#technology-stack)
10. [Deployment Topology (Cloud.gov)](#deployment-topology-cloudgov)
11. [Migration Strategy (8-Week MVP)](#migration-strategy-8-week-mvp)
12. [Risks and Mitigations](#risks-and-mitigations)
13. [Open Questions and Required Decisions](#open-questions-and-required-decisions)

---

## Executive Summary

This document defines the target architecture for replacing Django admin workflows with a React-based admin console while keeping Django as the system-of-record backend.

The primary recommendation is a standalone Next.js admin application that:

- uses server-side rendering and server components for data-heavy admin workflows,
- reuses existing Django session/auth infrastructure,
- keeps business rules, authorization enforcement, workflow transitions, and audit behavior in Django,
- is deployed as a separate Cloud.gov app alongside the existing user frontend and backend.

The first release should be an 8-week MVP focused on high-value workflows, not full Django admin parity.

---

## Decision Snapshot (ADR Summary)

### Decision

Adopt a standalone Next.js admin console instead of adding admin routes into the existing CRA app.

### Options Considered

- Option A: Standalone Next.js admin app
- Option B: CRA-integrated admin routes in existing frontend

### Why this decision

- Better fit for server-driven, data-heavy admin screens
- Clear separation of user-facing and admin-facing concerns
- Independent deploy/scale characteristics for admin runtime
- Cleaner long-term architecture for incremental migration away from Django admin

### Important tradeoff

CRA integration can be faster for narrow short-term delivery, but increases long-term coupling and operational/product complexity.

---

## Problem Statement

Django admin is currently used for key administrative workflows but creates issues for scale, UX, accessibility consistency, and frontend maintainability.

Key pain points:

- data-heavy pages degrade as records and filters increase,
- customization is expensive and tied to Django admin internals,
- admin UX patterns are inconsistent with the React user-facing experience,
- Section 508 and USWDS consistency require ongoing workaround effort,
- engineering ownership is split across mismatched UI stacks.

Core workflows that must be supported:

- user access and account-change review workflows,
- data file submission review and reparse initiation,
- error and processing-status inspection,
- feature flag administration,
- audit log review and filtering.

---

## Architecture Scope and Principles

### Scope of this document

This is an architecture specification. It describes system structure, boundaries, and key design choices.

It intentionally does not prescribe implementation-level details such as full code scaffolds, middleware source code, or deployment manifest templates.

### Principles

1. Django remains authoritative for domain and security decisions.
2. Next.js is a presentation/orchestration layer, not a replacement backend.
3. Prefer API reuse over policy duplication.
4. Use BFF behavior only where it adds clear admin UX value.
5. Keep MVP scope narrow and production-usable.

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

Browser -> Next.js admin -> Django API -> PostgreSQL

Boundary rules:

- Next.js can shape or aggregate responses for admin views.
- Django owns permission checks, workflow transitions, and domain validation.
- Direct database access from Next.js is out of scope for MVP.
- Any exception to direct DB access requires separate architecture review.

Data access patterns by workflow:

- Read-heavy pages (lists/tables): server-rendered with server-side filtering and pagination.
- Workflow mutations (approve/reparse/update flags): explicit mutation endpoints with Django-side audit and policy enforcement.
- Large dataset navigation: paginated or cursor-based API interactions, not client-side bulk loading.

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

---

## Rendering and Interaction Model

Rendering strategy should align to workload type:

- SSR/RSC default: list, detail, and admin overview surfaces.
- Client interactivity only where needed: filters, modals, local UI controls.
- Server-driven pagination/filtering: large tables and search-heavy screens.
- Streaming/progressive loading: optional for high-latency sections and can follow MVP.

This keeps initial render cost off the browser and improves perceived performance on operational screens.

---

## Technology Stack

| Area | Choice | Notes |
|------|--------|-------|
| Framework | Next.js 14+ | App Router, SSR/RSC support |
| UI System | USWDS React | Required design/accessibility alignment |
| Forms | React Hook Form + schema validation | Client ergonomics with server-authoritative validation |
| Data Fetching | Server-first fetch patterns | Avoid client waterfalls |
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

## Migration Strategy (8-Week MVP)

### MVP objective

Deliver a production-usable admin slice, not full parity.

### Recommended MVP scope

- feature flag management,
- audit log viewing,
- user review and approval basics,
- data file submission review and reparse initiation.

### Defer to post-MVP

- full parsed-record parity,
- deep error-report investigation surfaces,
- advanced exports and reporting,
- real-time streaming updates,
- complete Django admin retirement.

### Phase outline

- Week 1: foundation, auth integration, deployment skeleton.
- Weeks 2-3: read-heavy views and shared admin UI primitives.
- Weeks 4-5: user-management MVP workflows.
- Weeks 6-7: submission review and reparse workflows.
- Week 8: hardening, accessibility verification, launch readiness.

---

## Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| MVP scope expansion into parity | High | Strict scope gate and backlog discipline |
| Performance regressions on large datasets | High | Server-driven pagination and filtering from day one |
| Auth/session edge-case defects | Medium | Explicit session-expiry and CSRF test matrix |
| BFF overgrowth into second backend | Medium | Boundary guardrails in design and review |
| Operational overhead from third app | Medium | Reuse existing deployment and monitoring practices |
| Accessibility drift | Medium | USWDS conformance plus automated checks in CI |

---

## Open Questions and Required Decisions

1. Which exact MVP workflows are in scope for the first production release, and which are explicitly deferred?
2. Will admin routing be a dedicated subdomain or a routed path behind a shared edge entry?
3. What is the required SLA/SLO baseline for admin list pages and workflow mutations?
4. Which admin actions require enhanced audit metadata beyond current backend behavior?
5. Do any workflows require near-real-time status updates in MVP, or can they be deferred?
6. What is the acceptance threshold for Django admin parity before deprecation milestones are approved?

---

**Document Version:** 2.0  
**Last Updated:** April 2026  
**Next Review Gate:** Architecture sign-off and MVP scope freeze
