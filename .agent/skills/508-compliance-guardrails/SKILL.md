---
name: 508-compliance-guardrails
description: Enforce 508 compliance for user-facing components, including images, accordions, modals, alerts, and form inputs.
---

# Rule: 508 Compliance Guardrails

- All user-facing image layouts generated must include a meaningful, non-generic `alt` tag.
- Accordions, Modals, and Alert components must contain corresponding `aria-expanded`,
  `aria-controls`, and `role` attributes as outlined by USWDS guidelines.
- Form inputs must be explicitly mapped to `<Label>` components using matching `id` and `htmlFor` props.
