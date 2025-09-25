# WIP Dashboard Improvement Plan

Date: 2025-08-15 09:35 (+02:00)
Scope: `wip_dashboard_new/`

## 1) Objective
Deliver a performant, secure, and maintainable WIP Inventory Dashboard without compromising existing functionality. Focus areas:
- SQL query performance and stability
- Backend API design, caching, and security
- Frontend data handling and rendering performance

## 2) Current Architecture (confirmed)
- Frontend: React + Vite + TypeScript, MUI + DataGrid, Recharts, custom `src/theme.ts`
  - Routes: `src/routes.tsx` → `Dashboard`, `Tables`, `Reports`, `Suppliers`, `WIPPage`
  - Dashboards: `src/InventoryDashboard.tsx`, `src/components/WIPDashboard.tsx`
- Backend: `server.js` (Express + mssql) exposes `/api/inventory`, `/api/wip`
- SQL: `inventory_query.sql` with multiple CTEs and joins

## 3) Risks and Bottlenecks (summary)
- Complex SQL may cause slow responses and heavy scans/sorts
- In-memory caching only; large raw datasets shipped to client
- Client-side aggregations for charts; DataGrid uses client-only pagination
- Hardcoded DB credentials in `server.js`

## 4) Phased Plan with Detailed Steps and Expected Outcomes

### Phase 1 — Security & Infra Quick Wins (Low risk)

1. Move secrets to environment variables
   - Changes: `server.js`
     - Install `dotenv` and load `.env`
     - Replace hardcoded DB config (server/user/password/database) with `process.env.*`
     - Add `.env.example` (no secrets) to document required vars
   - Expected outcomes:
     - Credentials removed from source
     - Safer config management and portability

2. Add compression and security headers
   - Changes: `server.js`
     - Add `compression()` and `helmet()` middleware
     - Keep CORS minimal (if needed only for dev)
   - Expected outcomes:
     - Smaller payloads over the wire
     - Baseline security hardening

3. Structured logging with timings
   - Changes: `server.js`
     - Log per-request method, path, status, duration
     - Log DB query start/end, rows, duration, cache hit/miss
   - Expected outcomes:
     - Baseline performance visibility to guide later optimizations

4. Response hygiene
   - Changes: `server.js`
     - Consistent JSON shape: `{ success, data, error, timestamp }`
     - ETag enabled, proper cache-control where applicable
   - Expected outcomes:
     - Easier client consumption, better cache behavior

---

### Phase 2 — API Ergonomics, Aggregations, and Caching

1. Add pre-aggregated endpoints for WIP charts
   - New endpoints (examples):
     - `GET /api/wip/top-items?limit=20` → `[ { item_number, wip_value } ]`
     - `GET /api/wip/by-project` → `[ { project, wip_value } ]`
     - `GET /api/wip/by-type` → `[ { type, wip_value } ]`
     - `GET /api/wip/top-suppliers?limit=15&topItems=5` → `[ { supplier, items:[{ item, value }], others } ]`
   - Implementation notes:
     - Reuse or refactor `inventory_query.sql` into smaller targeted queries or views
     - Add per-endpoint in-memory TTL cache (5–15 min) keyed by params
   - Expected outcomes:
     - Far smaller payloads and faster client renders
     - Lower server CPU from reduced client-side aggregations

2. Server-side pagination and filters for inventory
   - Update `/api/inventory` to accept `offset`, `limit`, `search`, `project`, `supplier`, `type`
   - Return `{ rows, total }` for DataGrid server-side pagination
   - Expected outcomes:
     - Substantially reduced response sizes and memory usage on client

3. Network optimizations
   - Ensure gzip/etag are effective for JSON
   - Validate proxy setup for dev (`vite.config.ts`)
   - Expected outcomes:
     - Faster perceived performance and lower bandwidth

---

### Phase 3 — Frontend Integration & Perf

1. Switch WIP charts to new endpoints
   - Changes: `src/pages/WIPPage.tsx`, `src/components/WIPDashboard.tsx`
   - Replace client-side aggregation with direct consumption of aggregated API responses
   - Expected outcomes:
     - Reduced render time and JS main-thread work

2. Debounce global search in Navbar
   - Changes: `src/components/Navbar.tsx`
   - Debounce dispatch of `inventory-search` event by ~300ms
   - Expected outcomes:
     - Fewer unnecessary recomputations and re-renders

3. Code-splitting heavy routes
   - Changes: `src/App.tsx` or `src/routes.tsx`
   - Use `React.lazy` + `Suspense` for `Reports` and `Suppliers`
   - Expected outcomes:
     - Smaller initial bundle, faster first paint

4. Recharts polish
   - Ensure category limits, rotated labels, and “Others” bucketing where appropriate
   - Expected outcomes:
     - Clearer visuals and better responsiveness

---

### Phase 4 — SQL Performance Tuning

1. Capture actual execution plans and metrics
   - Run with `SET STATISTICS IO, TIME ON` and collect Actual Execution Plans
   - Target query: `inventory_query.sql`
   - Expected outcomes:
     - Identification of heavy scans, key lookups, and join hotspots

2. Index recommendations
   - Candidate indexes (to validate with plans and usage):
     - Join/filter keys on part/item tables (e.g., Item_Number)
     - Grouping keys used in aggregations (e.g., `Item_Project`, `Item_Supplier`, `FG_SFG_RM`)
     - WIP-related keys (areas/status columns used in CTEs)
     - Use INCLUDE columns to cover common select lists
   - Expected outcomes:
     - Reduced logical reads and query duration

3. Consider summary tables or indexed views
   - Precompute common WIP aggregates for the chart endpoints
   - Refresh strategy: nightly job or on-demand
   - Expected outcomes:
     - Consistent low-latency responses for dashboards

---

### Phase 5 — Hardening & Quality

1. Input validation for API
   - Add `zod` or `express-validator` for query/path params
   - Expected outcomes:
     - Safer endpoints and clearer error messages

2. Abort/cancel long-running requests
   - Use `AbortController` on server and client (where applicable)
   - Expected outcomes:
     - Freed resources when users navigate away; fewer zombie requests

3. Rate limiting and monitoring
   - Add basic rate limiting for public endpoints (if needed)
   - Add minimal monitoring/log aggregation
   - Expected outcomes:
     - Stability under load and observability for incidents

## 5) Acceptance Criteria / KPIs
- Backend:
  - 50–80% reduction in payload size for WIP endpoints (after aggregation)
  - P95 response time for WIP endpoints < 1.0s on representative data
  - Cache hit rate > 60% for chart endpoints under steady usage
- SQL:
  - Main WIP query logical reads and duration reduced measurably (>30%) or shifted to summary paths
- Frontend:
  - Initial route bundle size reduced via lazy loading
  - Noticeably smoother chart rendering with large category sets

## 6) Deliverables
- `.env.example` and updated `server.js` using env vars
- New aggregated WIP API endpoints with TTL caching
- Updated table endpoints supporting server-side pagination
- Frontend updated to use new endpoints and debounced search
- SQL plan analysis notes and index proposals

## 7) Rollback Plan
- Keep feature flags or route params to fall back to legacy raw endpoints
- Maintain a separate branch during rollout; merge after verification
- Revert new indexes if regressions observed (validated by plans and metrics)

## 8) Estimated Effort (rough)
- Phase 1: 0.5–1 day
- Phase 2: 1.5–3 days
- Phase 3: 1–2 days
- Phase 4: 2–4 days (dependent on DBA access and data volume)
- Phase 5: 0.5–1 day

## 9) Checklist
- [ ] Env vars + dotenv wired
- [ ] Compression + helmet enabled
- [ ] Logging + timings in place
- [ ] Aggregated WIP endpoints live (top items, by project, by type, top suppliers)
- [ ] Inventory endpoint supports server-side pagination
- [ ] Frontend consumes aggregated endpoints
- [ ] Debounced search in Navbar
- [ ] Route-level code splitting
- [ ] SQL execution plans captured and indexed
- [ ] Summary tables/indexed views evaluated
- [ ] Validation, rate limiting, and abort semantics added
