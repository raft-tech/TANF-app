---
name: react-uswds-component-enforcement
description: Enforce the use of React-USWDS components and prevent raw HTML/JSX with "usa-" class names.
---

# Rule: React-USWDS Component Enforcement

- NEVER write raw HTML/JSX with "usa-" class names unless explicitly asked.
- ALWAYS import wrappers directly from `@trussworks/react-uswds` using ES6 syntax.
- If a component is missing from `@trussworks/react-uswds`, scaffold a custom component
  matching the exact structural markup found in the official USWDS 3.0 documentation.
