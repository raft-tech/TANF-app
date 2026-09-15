---
name: script-conflict-mitigation
description: USWDS-specific guidance to prevent conflicts arising from multiple script imports and enforce proper script loading practices.
---

# Rule: Script Conflict Mitigation

- Do NOT import the global `uswds.js` or `uswds.min.js` bundles into individual components.
<!-- - Rely strictly on React synthetic events or `@trussworks/react-uswds` inner state management. -->
- For vanilla asset configurations, strictly isolate loading to the `App` mount tier or root layout lifecycle.
