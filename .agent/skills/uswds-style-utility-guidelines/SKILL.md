---
name: uswds-style-utility-guidelines
description: Enforce the use of USWDS style utility classes and prevent inline styles with absolute values.
---

# Rule: USWDS Style Utility Guidelines
- NEVER write inline style objects with absolute hex codes or raw pixel values (e.g., style={{ padding: '16px' }}).
- Use USWDS utility classes via the `className` prop to apply spacing, layout, and colors.
- Follow the exact USWDS token structure:
  - Spacing: Use `units-` (e.g., `margin-bottom-{units}`)
  - Colors: Use functional tokens (e.g., `bg-primary`, `text-ink`) instead of base colors.
