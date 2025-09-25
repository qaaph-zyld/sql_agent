# QADEE2798 Performance Recommendations

This document provides performance recommendations for common database operations.

## Indexing Recommendations

The following indexes are recommended for optimal performance:

### Inventory Table (15)

| Index Name | Columns | Type | Description |
|------------|---------|------|-------------|
| IX_15_part_site | in_part, in_site | Clustered | Primary lookup for inventory by part and site |
| IX_15_qty_oh | in_qty_oh | Non-clustered | Helps with queries filtering by on-hand quantity |
| IX_15_rop | in_rop, in_qty_oh | Non-clustered | Optimizes low inventory queries |

### Transaction History Table (tr_hist)

| Index Name | Columns | Type | Description |
|------------|---------|------|-------------|
| IX_tr_hist_part_date | tr_part, tr_date | Clustered | Primary lookup for transactions by part and date |
| IX_tr_hist_date | tr_date | Non-clustered | Helps with date range queries |
| IX_tr_hist_type | tr_type, tr_date | Non-clustered | Optimizes queries filtering by transaction type |

### Sales Order Tables (so_mstr, sod_det)

| Index Name | Columns | Type | Description |
|------------|---------|------|-------------|
| IX_so_mstr_cust | so_cust, so_ord_date | Non-clustered | Helps with customer-specific order queries |
| IX_so_mstr_date | so_ord_date | Non-clustered | Optimizes date range queries |
| IX_sod_det_part | sod_part, sod_nbr | Non-clustered | Helps with part-specific order queries |

## Query Optimization Tips

### Filtering

- Always include specific filters on indexed columns
- Use date ranges instead of open-ended date filters
- Filter early in the query to reduce the working set
- Use IN clauses with limited values instead of OR conditions

### Joins

- Join tables on indexed columns
- Use INNER JOIN instead of LEFT JOIN when possible
- Join only the tables needed for the query
- Consider denormalizing frequently joined data

### Aggregation

- Filter before aggregating
- Use indexed columns in GROUP BY clauses
- Consider pre-aggregating commonly used metrics
- Use HAVING only for filtering aggregated results

