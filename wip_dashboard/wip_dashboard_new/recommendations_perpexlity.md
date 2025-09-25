# Inventory Dashboard UI Recommendations (Open-Source)

Date: 2025-08-11
Scope: wip_dashboard_new/

## Summary
Several open-source, free-to-use UI solutions are suitable for a clean, responsive inventory dashboard with a data table, charts, and a refresh button. The most pragmatic choice for our current React setup is Material UI (MUI) with MUI X DataGrid, keeping Recharts for charts. This delivers a professional table (sorting, pagination, accessibility) and a cohesive component set.

## Options Considered
- React + Material UI (MUI)
  - Pros: Rich component set, strong accessibility, theming, DataGrid for tabular data, active community.
  - Cons: Adds dependency weight; design language is opinionated.
- Tailwind CSS + Headless UI / shadcn/ui
  - Pros: Highly flexible styling, modern look, good accessibility primitives.
  - Cons: More custom wiring for tables (feature parity requires extra work or third-party DataGrid).
- Next.js framework
  - Pros: SSR/SSG capabilities, good DX.
  - Cons: Project is Vite-based already; switching frameworks not justified for this local dashboard.

## Chosen Approach
- Keep current stack (Vite + React + TypeScript + Recharts).
- Add MUI for UI polish and accessibility.
- Replace HTML table with MUI X DataGrid for robust tabular UX.
- Preserve current sidebar and charts; iterate visually as needed.

## Immediate Conclusions to Implement
1. Integrate MUI DataGrid for the inventory table with pagination, compact density, and formatters for currency and integers.
2. Use MUI Alert for error feedback (replacing raw error div).
3. Keep the existing Refresh button for now; optionally convert to MUI Button in a later pass.
4. Ensure the page title is updated to the requested "Inventory Dashboard 2798".

## Next Iterations (Optional)
- Migrate controls (filters, refresh) to MUI components (Select, Button, FormControl).
- Add MUI layout (Grid, Card) to refine spacing and visual consistency.
- Introduce a lightweight notification (Snackbar) for refresh success/failure.
- Theme polish for better visual parity with provided screenshots.

## Dependencies to Add
- @mui/material
- @mui/icons-material (optional, if we switch to MUI icons)
- @emotion/react and @emotion/styled (peer deps for MUI)
- @mui/x-data-grid (community edition DataGrid)

Install (PowerShell):
```
npm i @mui/material @mui/icons-material @emotion/react @emotion/styled @mui/x-data-grid
```

## Validation Checklist
- DataGrid renders first 100 filtered rows, supports pagination and keyboard nav.
- Currency and numbers are formatted consistently with existing helpers.
- Charts and filters continue to function.
- Refresh flow remains unchanged.
- Title reads: "Inventory Dashboard 2798".
